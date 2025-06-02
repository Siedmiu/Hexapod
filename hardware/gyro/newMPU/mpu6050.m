function mpu6050_path_tracking()
    comPort = 'COM4';      % CHECK YOUR COM PORT IN DEVICE MANAGER
    baudRate = 115200;
    readDuration = 120;    % testing time in seconds
    plotRefreshRate = 10;
    
    % base Madgwick filter Algorithm parameters
    betaBase = 0.1;        % Madgwick filter gain
    betaHigh = 0.3;        % Higher gain = faster convergence during motion
    betaLow = 0.05;        % Lower gain = better stability
    
    % ZUPT and drift mitigation
    zuptAccelThreshold = 0.15;  % m/s²
    zuptGyroThreshold = 0.05;   % rad/s
    zuptCounterThreshold = 5;   % hysteresis steps
    stillnessDecay = 0.95;      
    % Drift mitigation
    velocityDampingFactor = 0.996;  % damping
    positionDampingFactor = 0.999;  % position damping
    
    % State variables
    timestamps = [];
    quaternions = [];
    eulerAngles = [];
    rawAccelerations = [];
    worldAccelerations = [];
    gyroscopeData = [];
    positions = [0, 0, 0];  % [x, y, z]
    velocities = [0, 0, 0]; % [vx, vy, vz]
    path = [0, 0, 0];       % Initial path point
    velHistory = [];
    stillnessCounter = 0;
    
    % Gravity
    gravityMagnitude = 9.81;
    isCalibrated = false;
    calibrationSamples = [];
    calibrationPeriod = 2;  % calibration time in seconds
    calibrationStartTime = 0;
    waitingForInit = true;
    
    % Create figure
    figHandle = figure('Name', 'MPU6050 Path Tracking', 'NumberTitle', 'off', 'Position', [100, 100, 1200, 800]);
    set(figHandle, 'DeleteFcn', @figureClosedCallback);
    figureAlive = true;
    
    % 3D Path plot
    subplot(2, 3, [1, 4]); 
    pathPlot = plot3(0, 0, 0, 'r-', 'LineWidth', 2);
    title('3D Path Tracking'); 
    xlabel('X (m)'); ylabel('Y (m)'); zlabel('Z (m)'); 
    grid on; axis equal; hold on;
    currentPosPlot = plot3(0, 0, 0, 'bo', 'MarkerFaceColor', 'b', 'MarkerSize', 10);
    axesPlot = plotCoordinateSystem([0 0 0], eye(3), 0.1);
    view(3); axis([-1 1 -1 1 -1 1]);
    
    % Orientation plot
    subplot(2, 3, 2);
    orientationPlot = plot3([0 0], [0 0], [0 0], 'b-', 'LineWidth', 2);
    title('Sensor Orientation');
    xlabel('X'); ylabel('Y'); zlabel('Z');
    grid on; axis equal; hold on;
    oriAxesPlot = plotCoordinateSystem([0 0 0], eye(3), 0.5);
    view(3);
    
    % Euler angles plot
    subplot(2, 3, 3); hold on;
    eulPlot = zeros(3, 1);
    eulPlot(1) = plot(0, 0, 'r-');
    eulPlot(2) = plot(0, 0, 'g-');
    eulPlot(3) = plot(0, 0, 'b-');
    title('Euler Angles'); xlabel('Time (s)'); ylabel('Degrees'); grid on;
    legend('Yaw', 'Pitch', 'Roll', 'Location', 'southeast');
    
    % Raw accelerations plot
    subplot(2, 3, 5); hold on;
    accelPlot = zeros(3, 1);
    accelPlot(1) = plot(0, 0, 'r-');
    accelPlot(2) = plot(0, 0, 'g-');
    accelPlot(3) = plot(0, 0, 'b-');
    title('Acceleration'); xlabel('Time (s)'); ylabel('m/s²'); grid on;
    legend('X', 'Y', 'Z', 'Location', 'southeast');
    
    % Velocity plot
    subplot(2, 3, 6); hold on;
    velPlot = zeros(3, 1);
    velPlot(1) = plot(0, 0, 'r-');
    velPlot(2) = plot(0, 0, 'g-');
    velPlot(3) = plot(0, 0, 'b-');
    title('Velocity'); xlabel('Time (s)'); ylabel('m/s'); grid on;
    legend('X', 'Y', 'Z', 'Location', 'southeast');
    
    %% Serial connection
    try
        if ~isempty(instrfind)
            fclose(instrfind);
            delete(instrfind);
        end
        s = serialport(comPort, baudRate);
        flush(s);
        disp(['Connected to ', comPort]);
        disp('Waiting for initialization period to complete...');
        
        startTime = tic;
        lastPlotUpdate = toc(startTime);
        lastTime = 0;
        
        %Madgwick filter instance
        madgwick = MadgwickAHRS('SamplePeriod', 1/100, 'Beta', betaBase);
        
        % Main loop
        while toc(startTime) < readDuration && figureAlive
            if s.NumBytesAvailable > 0
                line = readline(s);

                % information messages
                if contains(line, 'Initializing') || contains(line, 'Testing') || contains(line, 'connection') || contains(line, 'Enabling') || contains(line, 'DMP ready') || contains(line, 'Waiting') || contains(line, 'Setteling')
                    disp([strtrim(line)]);
                    continue;
                end
                
                if contains(line, 'INIT_COMPLETE')
                    waitingForInit = false;
                    calibrationStartTime = toc(startTime);
                    disp('Initialization period complete.');
                    disp(['Starting calibration for ', num2str(calibrationPeriod), ' seconds...']);
                    continue;
                end
                
                %process sensor data
                try
                    data = str2double(split(line, ','));
                    
                    if length(data) == 14
                        % Extract data
                        timestamp = data(1) / 1000; 
                        quat = reshape(data(2:5), 1, 4);      % w, x, y, z
                        euler = reshape(data(6:8), 1, 3);     % yaw, pitch, roll in degrees
                        rawAccel = reshape(data(9:11), 1, 3); % raw acceleration values
                        worldAccel = reshape(data(12:14), 1, 3); % world frame acceleration
                        
                        % accelerations to m/s²
                        accelScale = 9.81 / 16384;
                        worldAccel = worldAccel * accelScale;
                        
                        % Extract gyroscope data from quaternion
                        if size(quaternions, 1) > 0
                            lastQuat = quaternions(end, :);
                            gyro = 2 * quatMultiply(quatConj(lastQuat), quatDiff(lastQuat, quat, timestamp - lastTime));
                            gyro = gyro(2:4);
                        else
                            gyro = [0, 0, 0];
                        end
                        
                        if waitingForInit
                            continue;
                        end
                        
                        % Madgwick filter dynamic
                        try
                            if ~isempty(lastTime)
                                accelMagnitude = norm(worldAccel);
                                gyroMagnitude = norm(gyro);
                                isMoving = (accelMagnitude > zuptAccelThreshold) || (gyroMagnitude > zuptGyroThreshold);
                                
                                % Adjust beta
                                if isMoving
                                    madgwick.Beta = min(madgwick.Beta * 1.1, betaHigh);  % Increase gradually
                                else
                                    madgwick.Beta = max(madgwick.Beta * 0.95, betaLow);  % Decrease gradually
                                end
                            end
                            
                            madgwick.UpdateIMU(gyro, rawAccel);
                            filteredQuat = madgwick.Quaternion;
                        catch madgwickErr
                            disp(['Madgwick filter error: ', madgwickErr.message]);
                            filteredQuat = quat;
                        end
                        
                        % Store sensor data
                        timestamps(end+1) = timestamp;
                        quaternions(end+1, :) = quat;
                        eulerAngles(end+1, :) = euler;
                        rawAccelerations(end+1, :) = rawAccel;
                        worldAccelerations(end+1, :) = worldAccel;
                        gyroscopeData(end+1, :) = gyro;
                        
                        % calibration period
                        currentTime = toc(startTime);
                        if ~isCalibrated && (currentTime - calibrationStartTime < calibrationPeriod)
                            calibrationSamples(end+1, :) = worldAccel;  % Store scaled acceleration
                        elseif ~isCalibrated && (currentTime - calibrationStartTime >= calibrationPeriod)
                            % reference gravity vector
                            if ~isempty(calibrationSamples)
                                isCalibrated = true;
                                disp('Calibration complete. Starting path tracking...');
                            else
                                disp('Warning: No calibration samples collected.');
                                isCalibrated = true;
                            end
                        end
                        
                        if isCalibrated
                            if ~isempty(lastTime)
                                dt = timestamp - lastTime;
                                
                                % low-pass filter for noise reduction
                                alpha = 0.1;
                                if size(worldAccelerations, 1) > 1
                                    filteredAccel = alpha * worldAccel + (1-alpha) * worldAccelerations(end-1, :);
                                else
                                    filteredAccel = worldAccel;
                                end
                                
                                filteredAccel = reshape(filteredAccel, 1, 3);
                                
                                % Calculate gravity vector based on current orientation
                                R = quaternionToRotationMatrix(quat);
                                worldGravity = [0, 0, gravityMagnitude];
                                sensorGravity = (R' * worldGravity')';
                                
                                % Compensate for gravity
                                compensatedAccel = filteredAccel - sensorGravity;
                                
                                % ZUPT (Zero Velocity Update)
                                accelMagnitude = norm(compensatedAccel);
                                gyroMagnitude = norm(gyro);
                                
                                isStill = (accelMagnitude < zuptAccelThreshold) && (gyroMagnitude < zuptGyroThreshold);
                                if isStill
                                    stillnessCounter = min(stillnessCounter + 1, 10);  % Cap at 10
                                else
                                    stillnessCounter = max(stillnessCounter - 1, 0);   % Don't go below 0
                                end
                                
                                % drift mitigation
                                if stillnessCounter >= zuptCounterThreshold
                                    velocities = [0, 0, 0];
                                else                                  
                                    % Integrate acceleration -> velocity, aggressive damping
                                    velocities = velocities + compensatedAccel * dt;
                                    
                                    stillnessFactor = min(stillnessCounter / zuptCounterThreshold, 1);
                                    adaptiveDamping = velocityDampingFactor + (1 - velocityDampingFactor) * stillnessFactor;
                                    velocities = velocities * adaptiveDamping;
                                    
                                    velMagnitude = norm(velocities);
                                    if velMagnitude < 0.01  % 1 cm/s threshold
                                        velocities = [0, 0, 0];
                                    end
                                end
                                
                                % Integrate velocity -> position
                                positions = positions + velocities * dt;
                                positions = positions * positionDampingFactor;
                                path(end+1, :) = positions;
                            end
                            lastTime = timestamp;
                        end
                        
                        % Update visualization plots
                        currentTime = toc(startTime);
                        if (currentTime - lastPlotUpdate) > (1/plotRefreshRate) && figureAlive
                            try
                                positions = reshape(positions, 1, 3);
                                velocities = reshape(velocities, 1, 3);
                                updatePlots();
                                lastPlotUpdate = currentTime;
                                drawnow limitrate;
                            catch plotErr
                                disp(['Plot update error: ', plotErr.message]);
                                if ~ishandle(figHandle)
                                    figureAlive = false;
                                    disp('Figure was closed.');
                                end
                            end
                        end
                    else
                        disp(['Incorrect data format. Expected 14 elements, got ', num2str(length(data))]);
                    end
                catch dataErr
                    disp(['Data parsing error: ', dataErr.message]);
                end
            end
        end
        
        % Close serial connection
        clear s;
        disp('Data collection complete');
        
    catch ME
        disp('Error:');
        disp(ME.message);
        
        if exist('s', 'var')
            clear s;
        end
    end

    % Callback for figure closure
    function figureClosedCallback(~, ~)
        figureAlive = false;
        disp('Figure closed by user');
    end

    %% Update plots function
    function updatePlots()
        if isempty(timestamps) || ~figureAlive || ~ishandle(figHandle)
            return;
        end
        
        % Calculate relative time for x-axis
        relativeTime = timestamps - timestamps(1);
        
        % Update orientation visualization
        if ~isempty(quaternions) && all(ishandle(oriAxesPlot))
            try
                lastQuat = quaternions(end, :);
                R = quaternionToRotationMatrix(lastQuat);
                delete(oriAxesPlot);
                oriAxesPlot = plotCoordinateSystem([0 0 0], R, 0.5);
            catch err
                disp(['Orientation plot error: ', err.message]);
            end
        end
        
        % Update 3D path
        if isCalibrated && size(path, 1) > 1
            try
                set(pathPlot, 'XData', path(:, 1), 'YData', path(:, 2), 'ZData', path(:, 3));
                set(currentPosPlot, 'XData', positions(1), 'YData', positions(2), 'ZData', positions(3));
                
                if all(ishandle(axesPlot))
                    delete(axesPlot);
                    lastQuat = quaternions(end, :);
                    R = quaternionToRotationMatrix(lastQuat);
                    positions_row = reshape(positions, 1, 3);
                    axesPlot = plotCoordinateSystem(positions_row, R, 0.1);
                end
                
                % Adjust axis limits based on path size
                axisRange = max(max(abs(path)));
                if axisRange > 0
                    axisLimit = max(1, axisRange * 1.2);
                    axis([-axisLimit axisLimit -axisLimit axisLimit -axisLimit axisLimit]);
                end
            catch err
                disp(['Path plot error: ', err.message]);
            end
        end
        
        % Update euler angles plot
        if ~isempty(eulerAngles)
            try
                if size(eulerAngles, 1) > length(relativeTime)
                    eulerAngles = eulerAngles(end-length(relativeTime)+1:end, :);
                end
                
                for i = 1:3
                    if ishandle(eulPlot(i))
                        set(eulPlot(i), 'XData', relativeTime, 'YData', eulerAngles(:, i));
                    end
                end
            catch err
                disp(['Euler plot error: ', err.message]);
            end
        end
        
        % Update acceleration plot
        if isCalibrated && ~isempty(worldAccelerations)
            try
                if size(worldAccelerations, 1) > length(relativeTime)
                    worldAccelerations = worldAccelerations(end-length(relativeTime)+1:end, :);
                end
                
                % Get last orientation to calculate gravity in sensor frame
                lastQuat = quaternions(end, :);
                R = quaternionToRotationMatrix(lastQuat);
                worldGravity = [0, 0, gravityMagnitude];
                sensorGravity = (R' * worldGravity')';
                
                % Remove adaptive gravity component
                calibratedAccels = worldAccelerations - repmat(sensorGravity, size(worldAccelerations, 1), 1);
                
                for i = 1:3
                    if ishandle(accelPlot(i))
                        set(accelPlot(i), 'XData', relativeTime, 'YData', calibratedAccels(:, i));
                    end
                end
            catch err
                disp(['Acceleration plot error: ', err.message]);
            end
        end
        
        % Update velocity plot
        if isCalibrated && exist('velocities', 'var')
            try
                velocities_row = reshape(velocities, 1, 3);
                
                if isempty(velHistory)
                    velHistory = velocities_row;
                else
                    velHistory(end+1, :) = velocities_row;
                end
                
                if size(velHistory, 1) > length(relativeTime)
                    velHistory = velHistory(end-length(relativeTime)+1:end, :);
                end
                
                for i = 1:3
                    if ishandle(velPlot(i))
                        set(velPlot(i), 'XData', relativeTime, 'YData', velHistory(:, i));
                    end
                end
            catch err
                disp(['Velocity plot error: ', err.message]);
            end
        end
    end

    %% Convert quaternion to rotation matrix
    function R = quaternionToRotationMatrix(q)
        q = reshape(q, 1, 4);
        
        w = q(1);
        x = q(2);
        y = q(3);
        z = q(4);
        
        n = norm(q);
        if n > 0
            w = w/n;
            x = x/n;
            y = y/n;
            z = z/n;
        end
        
        R = zeros(3, 3);
        R(1, 1) = 1 - 2*y^2 - 2*z^2;
        R(1, 2) = 2*x*y - 2*w*z;
        R(1, 3) = 2*x*z + 2*w*y;
        
        R(2, 1) = 2*x*y + 2*w*z;
        R(2, 2) = 1 - 2*x^2 - 2*z^2;
        R(2, 3) = 2*y*z - 2*w*x;
        
        R(3, 1) = 2*x*z - 2*w*y;
        R(3, 2) = 2*y*z + 2*w*x;
        R(3, 3) = 1 - 2*x^2 - 2*y^2;
    end

    %% Quaternion conjugate
    function qConj = quatConj(q)
        qConj = [q(1), -q(2), -q(3), -q(4)];
    end
    
    %% Quaternion multiplication
    function c = quatMultiply(a, b)
        a = reshape(a, 1, 4);
        b = reshape(b, 1, 4);
        
        c = zeros(1, 4);
        c(1) = a(1)*b(1) - a(2)*b(2) - a(3)*b(3) - a(4)*b(4);
        c(2) = a(1)*b(2) + a(2)*b(1) + a(3)*b(4) - a(4)*b(3);
        c(3) = a(1)*b(3) - a(2)*b(4) + a(3)*b(1) + a(4)*b(2);
        c(4) = a(1)*b(4) + a(2)*b(3) - a(3)*b(2) + a(4)*b(1);
    end
    
    %% Quaternion difference
    function diff = quatDiff(q1, q2, dt)
        % Calculate the rate of change of quaternion
        if dt > 0
            diff = (q2 - q1) / dt;
        else
            diff = [0, 0, 0, 0];
        end
    end

    %% Plot coordinate system axes
    function h = plotCoordinateSystem(origin, R, scale)
        origin = reshape(origin, 1, 3);
        
        xAxis = origin + scale * reshape(R(:, 1)', 1, 3);
        yAxis = origin + scale * reshape(R(:, 2)', 1, 3);
        zAxis = origin + scale * reshape(R(:, 3)', 1, 3);
        
        h(1) = plot3([origin(1) xAxis(1)], [origin(2) xAxis(2)], [origin(3) xAxis(3)], 'r-', 'LineWidth', 2);
        h(2) = plot3([origin(1) yAxis(1)], [origin(2) yAxis(2)], [origin(3) yAxis(3)], 'g-', 'LineWidth', 2);
        h(3) = plot3([origin(1) zAxis(1)], [origin(2) zAxis(2)], [origin(3) zAxis(3)], 'b-', 'LineWidth', 2);
    end
end