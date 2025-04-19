function mpu6050_visualization()
    %% Parameters
    comPort = 'COM4';      % Update this to your ESP32's COM port
    baudRate = 115200;     % Match this to your ESP32's serial baud rate
    readDuration = 30;     % Duration to read data in seconds
    plotRefreshRate = 10;  % Number of refreshes per second

    %% Initialize variables
    % Data arrays
    timestamps = [];
    quaternions = [];
    eulerAngles = [];
    rawAccelerations = [];
    worldAccelerations = [];

    % Figure handles
    figHandle = figure('Name', 'MPU6050 Data', 'NumberTitle', 'off', 'Position', [100, 100, 900, 600]);
    set(figHandle, 'DeleteFcn', @figureClosedCallback);
    figureAlive = true;

    % Create subplots
    subplot(2,2,1); 
    orientationPlot = plot3(0,0,0, 'r-', 'LineWidth', 2); 
    title('3D Orientation'); 
    xlabel('X'); ylabel('Y'); zlabel('Z'); grid on; axis equal; hold on;
    axesPlot = plotCoordinateSystem([0 0 0], eye(3), 0.5);
    view(3);

    % Create 3 lines each for Euler angles, raw accelerations, and world accelerations
    subplot(2,2,2); hold on;
    eulPlot = zeros(3,1);
    eulPlot(1) = plot(0, 0, 'r-');
    eulPlot(2) = plot(0, 0, 'g-');
    eulPlot(3) = plot(0, 0, 'b-');
    title('Euler Angles'); xlabel('Time (s)'); ylabel('Degrees'); grid on;
    legend('Yaw', 'Pitch', 'Roll', 'Location', 'southeast');

    % Raw accelerations plot
    subplot(2,2,3); hold on;
    rawAccelPlot = zeros(3,1);
    rawAccelPlot(1) = plot(0, 0, 'r-');
    rawAccelPlot(2) = plot(0, 0, 'g-');
    rawAccelPlot(3) = plot(0, 0, 'b-');
    title('Raw Acceleration'); xlabel('Time (s)'); ylabel('Raw Units'); grid on;
    legend('X', 'Y', 'Z', 'Location', 'southeast');

    % World accelerations plot
    subplot(2,2,4); hold on;
    worldAccelPlot = zeros(3,1);
    worldAccelPlot(1) = plot(0, 0, 'r-');
    worldAccelPlot(2) = plot(0, 0, 'g-');
    worldAccelPlot(3) = plot(0, 0, 'b-');
    title('World Acceleration'); xlabel('Time (s)'); ylabel('Raw Units'); grid on;
    legend('X', 'Y', 'Z', 'Location', 'southeast');

    %% Open serial connection
    try
        % Clear any existing serial connections
        if ~isempty(instrfind)
            fclose(instrfind);
            delete(instrfind);
        end
        
        % Create serial connection
        s = serialport(comPort, baudRate);
        flush(s);
        disp(['Connected to ', comPort]);
        
        % Initialize timing
        startTime = tic;
        lastPlotUpdate = toc(startTime);
        
        % Main loop
        while toc(startTime) < readDuration && figureAlive
            if s.NumBytesAvailable > 0
                % Read data
                line = readline(s);
                try
                    data = str2double(split(line, ','));
                    
                    % Check if we have the correct number of elements
                    % Format: timestamp, 4 quaternion, 3 euler angles, 3 raw accel, 3 world accel
                    if length(data) == 14  
                        % Parse data
                        timestamp = data(1) / 1000;  % Convert to seconds
                        quat = data(2:5);            % w, x, y, z
                        euler = data(6:8);           % yaw, pitch, roll in degrees
                        rawAccel = data(9:11);       % raw acceleration values
                        worldAccel = data(12:14);    % world frame acceleration
                        
                        % Store data
                        timestamps(end+1) = timestamp;
                        quaternions(end+1,:) = quat;
                        eulerAngles(end+1,:) = euler;
                        rawAccelerations(end+1,:) = rawAccel;
                        worldAccelerations(end+1,:) = worldAccel;
                        
                        % Update plots periodically
                        currentTime = toc(startTime);
                        if (currentTime - lastPlotUpdate) > (1/plotRefreshRate) && figureAlive
                            try
                                updatePlots();
                                lastPlotUpdate = currentTime;
                                drawnow limitrate;
                            catch plotErr
                                disp(['Plot update error: ', plotErr.message]);
                                % Check if figure still exists
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
        
        % Close the serial connection
        clear s;
        disp('Data collection complete');
        
    catch ME
        % Error handling
        disp('Error:');
        disp(ME.message);
        
        % Clean up
        if exist('s', 'var')
            clear s;
        end
    end

    %% Callback for figure closure
    function figureClosedCallback(~, ~)
        figureAlive = false;
        disp('Figure closed by user');
    end

    %% Nested Functions
    function updatePlots()
        % Check if we have enough data and if figure still exists
        if length(timestamps) < 2 || ~figureAlive || ~ishandle(figHandle)
            return;
        end
        
        % Get relative timestamps for plotting
        relativeTime = timestamps - timestamps(1);
        
        % Update orientation visualization
        if ~isempty(quaternions) && all(ishandle(axesPlot))
            try
                lastQuat = quaternions(end,:);
                R = quaternionToRotationMatrix(lastQuat);
                delete(axesPlot);
                axesPlot = plotCoordinateSystem([0 0 0], R, 0.5);
            catch
                % Continue if orientation plot fails
            end
        end
        
        % Update euler angles plot
        if ~isempty(eulerAngles)
            for i = 1:3
                if ishandle(eulPlot(i))
                    try
                        set(eulPlot(i), 'XData', relativeTime, 'YData', eulerAngles(:,i));
                    catch
                        % Continue if this plot fails
                    end
                end
            end
        end
        
        % Update raw acceleration plot
        if ~isempty(rawAccelerations)
            for i = 1:3
                if ishandle(rawAccelPlot(i))
                    try
                        set(rawAccelPlot(i), 'XData', relativeTime, 'YData', rawAccelerations(:,i));
                    catch
                        % Continue if this plot fails
                    end
                end
            end
        end
        
        % Update world acceleration plot
        if ~isempty(worldAccelerations)
            for i = 1:3
                if ishandle(worldAccelPlot(i))
                    try
                        set(worldAccelPlot(i), 'XData', relativeTime, 'YData', worldAccelerations(:,i));
                    catch
                        % Continue if this plot fails
                    end
                end
            end
        end
    end

    function R = quaternionToRotationMatrix(q)
        % Convert quaternion to rotation matrix
        % Input: q = [w, x, y, z] quaternion
        % Output: R = 3x3 rotation matrix
        
        w = q(1);
        x = q(2);
        y = q(3);
        z = q(4);
        
        % Normalize quaternion
        n = norm(q);
        if n > 0
            w = w/n;
            x = x/n;
            y = y/n;
            z = z/n;
        end
        
        % Compute rotation matrix elements
        R = zeros(3,3);
        R(1,1) = 1 - 2*y^2 - 2*z^2;
        R(1,2) = 2*x*y - 2*w*z;
        R(1,3) = 2*x*z + 2*w*y;
        
        R(2,1) = 2*x*y + 2*w*z;
        R(2,2) = 1 - 2*x^2 - 2*z^2;
        R(2,3) = 2*y*z - 2*w*x;
        
        R(3,1) = 2*x*z - 2*w*y;
        R(3,2) = 2*y*z + 2*w*x;
        R(3,3) = 1 - 2*x^2 - 2*y^2;
    end

    function h = plotCoordinateSystem(origin, R, scale)
        % Create a coordinate system visualization
        % Returns handles to the three lines
        
        % Define the three axes
        xAxis = origin + scale * R(:,1)';
        yAxis = origin + scale * R(:,2)';
        zAxis = origin + scale * R(:,3)';
        
        % Plot the three axes
        h(1) = plot3([origin(1) xAxis(1)], [origin(2) xAxis(2)], [origin(3) xAxis(3)], 'r-', 'LineWidth', 2);
        h(2) = plot3([origin(1) yAxis(1)], [origin(2) yAxis(2)], [origin(3) yAxis(3)], 'g-', 'LineWidth', 2);
        h(3) = plot3([origin(1) zAxis(1)], [origin(2) zAxis(2)], [origin(3) zAxis(3)], 'b-', 'LineWidth', 2);
    end
end