% Madgwick AHRS Algorithm Implementation
% https://github.com/xioTechnologies/Fusion
classdef MadgwickAHRS < handle
    properties
        SamplePeriod = 1/256;
        Quaternion = [1 0 0 0];
        Beta = 1;
    end
    
    methods
        function obj = MadgwickAHRS(varargin)
            for i = 1:2:nargin
                if strcmp(varargin{i}, 'SamplePeriod'), obj.SamplePeriod = varargin{i+1};
                elseif strcmp(varargin{i}, 'Beta'), obj.Beta = varargin{i+1};
                end
            end
        end
        
        function obj = UpdateIMU(obj, Gyroscope, Accelerometer)
            q = reshape(obj.Quaternion, 1, 4);
            Gyroscope = reshape(Gyroscope, 1, 3);
            Accelerometer = reshape(Accelerometer, 1, 3);
            
            % Normalise accelerometer measurement
            accel_norm = norm(Accelerometer);
            if(accel_norm == 0), return; end
            Accelerometer = Accelerometer / accel_norm;    % normalise magnitude
            
            % Gradient descent algorithm corrective step
            F = [2*(q(2)*q(4) - q(1)*q(3)) - Accelerometer(1);
                 2*(q(1)*q(2) + q(3)*q(4)) - Accelerometer(2);
                 2*(0.5 - q(2)^2 - q(3)^2) - Accelerometer(3)];
            
            J = [-2*q(3),                 2*q(4),                  -2*q(1),                  2*q(2);
                  2*q(2),                 2*q(1),                   2*q(4),                  2*q(3);
                  0,                     -4*q(2),                  -4*q(3),                  0    ];
            
            step = (J'*F);
            step_norm = norm(step);
            if(step_norm ~= 0)
                step = step / step_norm;    % normalise step magnitude
            end
            
            step = reshape(step, 1, 4);
            
            % Compute rate of change of quaternion
            qDot = 0.5 * quaternProd(q, [0 Gyroscope(1) Gyroscope(2) Gyroscope(3)]) - obj.Beta * step;
            
            % Integrate to yield quaternion
            q = q + qDot * obj.SamplePeriod;
            q_norm = norm(q);
            if(q_norm ~= 0)
                q = q / q_norm; % normalise quaternion
            end
            
            obj.Quaternion = reshape(q, 1, 4);
        end
    end
end

function c = quaternProd(a, b)
    a = reshape(a, 1, 4);
    b = reshape(b, 1, 4);
    
    ab = a(1)*b(1) - a(2)*b(2) - a(3)*b(3) - a(4)*b(4);
    qx = a(1)*b(2) + a(2)*b(1) + a(3)*b(4) - a(4)*b(3);
    qy = a(1)*b(3) - a(2)*b(4) + a(3)*b(1) + a(4)*b(2);
    qz = a(1)*b(4) + a(2)*b(3) - a(3)*b(2) + a(4)*b(1);
    c = [ab qx qy qz];
end