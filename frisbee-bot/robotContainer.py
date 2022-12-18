import wpilib
import commands2
import commands2.cmd
import commands2.button
import wpimath.controller
import subsystems.DriveSubsystem
import subsystems.ShooterSubsystem
import constants

# This class is where the bulk of the robot should be declared. Since Command-based is a
# "declarative" paradigm, very little robot logic should actually be handled in the {@link Robot}
# periodic methods (other than the scheduler calls). Instead, the structure of the robot (including
# subsystems, commands, and button mappings) should be declared here.


class RobotContainer():

    def __init__(self):
        self.robotDrive = subsystems.DriveSubsystem.DriveSubsystem()
        self.shooter = subsystems.ShooterSubsystem.ShooterSubsystem(wpimath.controller.PIDController(
            constants.Constants.ShooterConstants.kP,
            constants.Constants.ShooterConstants.kI,
            constants.Constants.ShooterConstants.kD,
        ))

        self.shooter.ShooterSubsystemSetup()
        self.robotDrive.DriveSubsystemSetup()

        self.spinUpShooter = commands2.cmd.runOnce(self.shooter.enable, [self.shooter])
        self.stopShooter = commands2.cmd.runOnce(self.shooter.disable, [self.shooter])

        # An autonomous routine that shoots the loaded frisbees
        self.autonomousCommand = commands2.cmd.sequence([
            #Start the command by spinning up the shooter...
            commands2.cmd.runOnce(self.shooter.enable, [self.shooter]),
            #Wait until the shooter is at speed before feeding the frisbees
            commands2.cmd.waitUntil(lambda: self.shooter.getController().atSetpoint()),
            #Start running the feeder
            commands2.cmd.runOnce(self.shooter.runFeeder, [self.shooter]),
            #Shoot for the specified time
            commands2.cmd.wait(constants.Constants.AutoConstants.kAutoShootTimeSeconds)
            #Add a timeout (will end the command if, for instance, the shooter
            #never gets up to speed)
            .withTimeout(constants.Constants.AutoConstants.kAutoTimeoutSeconds)
            #hen the command ends, turn off the shooter and the feeder
            .andThen(
                commands2.cmd.runOnce(
                    lambda: self.shooter.disable, [self.shooter]
                ).andThen(
                    commands2.cmd.runOnce(
                    lambda: self.shooter.stopFeeder, [self.shooter]
                )
                )
            )
        ]
        )

        #The driver's controller
        self.driverController = commands2.button.CommandXboxController(constants.Constants.OIConstants.kDriverControllerPort)

    # The container for the robot. Contains subsystems, OI devices, and commands.
    def robotContainer(self):
        #Configure the button bindings
        self.configureButtonBindings()

        #Configure default commands
        #Set the default drive command to split-stick arcade drive
        self.robotDrive.setDefaultCommand(
            #A split-stick arcade command, with forward/backward controlled by the left
            #hand, and turning controlled by the right.
            commands2.cmd.run(
                lambda: self.robotDrive.arcadeDrive(
                    -self.driverController.getLeftY(), -self.driverController.getRightX()
                ),
                [self.robotDrive]
            )
        )

    #Use this method to define your button->command mappings. Buttons can be created via the button
    #factories on commands2.button.CommandGenericHID or one of its
    #subclasses (commands2.button.CommandJoystick or command2.button.CommandXboxController).
    def configureButtonBindings(self):
        # Configure your button bindings here

        # We can bind commands while retaining references to them in RobotContainer

        # Spin up the shooter when the 'A' button is pressed
        self.driverController.A().onTrue(self.spinUpShooter)

        # Turn off the shooter when the 'B' button is pressed
        self.driverController.B().onTrue(self.stopShooter)

        #We can also write them as temporary variables outside the bindings

        #Shoots if the shooter wheel has reached the target speed
        shoot = commands2.cmd.either(
            # Run the feeder
            commands2.cmd.runOnce(self.shooter.runFeeder, [self.shooter]),
            # Do nothing
            commands2.cmd.nothing(),
            # Determine which of the above to do based on whether the shooter has reached the
            # desired speed
            lambda: self.shooter.getController().atSetpoint()
        )

        stopFeeder = commands2.cmd.runOnce(self.shooter.stopFeeder, [self.shooter])

        # Shoot when the 'X' button is pressed
        self.driverController.X().onTrue(shoot).onFalse(stopFeeder)

        #We can also define commands inline at the binding!

        #While holding the shoulder button, drive at half speed
        self.driverController.rightBumper().onTrue(commands2.cmd.runOnce(self.robotDrive.maxOutputHalf, [self.robotDrive])).onFalse(commands2.cmd.runOnce(self.robotDrive.maxOutputFull, [self.robotDrive]))
    
    # Use this to pass the autonomous command to the main {@link Robot} class.
    def getAutonomousCommand(self) -> commands2.Command:
        """
        @return the command to run in autonomous
        """
        return self.autonomousCommand