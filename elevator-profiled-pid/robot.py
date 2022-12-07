import wpilib
import wpimath.controller
import wpimath.trajectory
import math


class MyRobot(wpilib.TimedRobot):

    kDt = 0.02

    joystick = wpilib.Joystick(1)
    encoder = wpilib.Encoder(1, 2)
    motor = wpilib.PWMSparkMax(1)

    # Create a PID controller whose setpoint's change is subject to maximum
    # velocity and acceleration constraints.
    constraints = wpimath.trajectory.TrapezoidProfile.Constraints(1.75, 0.75)
    controller = wpimath.controller.ProfiledPIDController(1.3, 0, 0.7, constraints, kDt)

    def robotInit(self) -> None:
        self.encoder.setDistancePerPulse(1 / 360 * 2 * math.pi * 1.5)

    def teleopPeriodic(self) -> None:
        if self.joystick.getRawButtonPressed(2):
            self.controller.setGoal(5)
        elif self.joystick.getRawButtonPressed(3):
            self.controller.setGoal(0)

        # Run controller and update motor output
        self.motor.set(self.controller.calculate(self.encoder.getDistance()))


if __name__ == "__main__":
    wpilib.run(MyRobot)
