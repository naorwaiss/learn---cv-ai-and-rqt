import pygame

# Initialize Pygame
pygame.init()

# Initialize the joystick module
pygame.joystick.init()

# Attempt to setup a joystick
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f"Joystick {joystick.get_name()} initialized")
else:
    print("No joystick detected. Please connect a joystick.")
    pygame.quit()
    exit()

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.JOYAXISMOTION:
            print(f"Joystick {event.joy} Axis {event.axis} motion: {event.value}")
        elif event.type == pygame.JOYBUTTONDOWN:
            print(f"Joystick {event.joy} Button {event.button} down")
        elif event.type == pygame.JOYBUTTONUP:
            print(f"Joystick {event.joy} Button {event.button} up")
        elif event.type == pygame.JOYHATMOTION:
            print(f"Joystick {event.joy} Hat {event.hat} motion: {event.value}")

# Quit Pygame
pygame.quit()