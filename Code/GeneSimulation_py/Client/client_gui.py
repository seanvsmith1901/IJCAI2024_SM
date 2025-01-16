import socket
import json
import pygame

SCREEN_WIDTH = 800 # https://www.youtube.com/watch?v=r7l0Rq9E8MY
SCREEN_HEIGHT = 800
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # establish screen as global so can draw from anywhere.



pygame.font.init()
font = pygame.font.Font(None, 32) # might need to dynamically allocate the font.
font_color = (0,0,0)
leaderboard_font = pygame.font.Font(None, 64)
leaderboard_font_color = (0,0,0)


BLACKCOLOR = (0, 0, 0)
WHITECOLOR = (255, 255, 255)
client_ID = 0
agents = [] # holds all of the sprites for the various agents.

input_rect = pygame.Rect(350, 150, 140, 32)
color_active = pygame.Color('lightskyblue3')
color_passive = pygame.Color('chartreuse4')
color = color_passive

def start_client():
    clock = pygame.time.Clock()
    username = False
    global client_ID
    #host = '192.168.30.17'  # The server's IP address
    host = '127.0.0.1'  # your local host address cause you're working from home.
    port = 12345         # The port number to connect to
    pygame.init()  # actually starts the game.
    # Create a TCP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connect to the server
    client_socket.connect((host, port))
    # Send data to the server


    # Receive a response from the server
    while True:
        if username != False:
            game_loop(client_socket)

        else: # they need to input a username
           username = set_username(client_socket, clock, username)


                    # Close the connection
    client_socket.close()


def game_loop(client_socket):
    global client_ID
    server_response = None
    data = client_socket.recv(65535)
    try:  # get the stuff first
        # Deserialize the JSON response from the server
        server_response = json.loads(data.decode())

    except json.JSONDecodeError:
        pass

    if server_response != None:
        print("This was the server response! ", server_response)

    message = {"NEW_INPUT" : "new_input"}
    client_socket.send(json.dumps(message).encode())  # send a packet on every frame.




# this just allows you to submit SOMETHING to the server which it can then tabulate. ITs called a username bc of old stuff. we could keep it that way
def set_username(client_socket, clock, username):
    user_text = ''
    active = False
    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_rect.collidepoint(event.pos):
                    active = True
                else:
                    active = False

            if event.type == pygame.KEYDOWN:
                # Check for backspace
                if event.key == pygame.K_BACKSPACE:

                    # get text input from 0 to -1 i.e. end.
                    user_text = user_text[:-1]

                    # Unicode standard is used for string
                # formation
                elif event.key == pygame.K_RETURN:
                    # send the packet!
                    message = {
                        "USERNAME": user_text,
                        "MESSAGE": "hello from the server!"
                    }
                    client_socket.send(json.dumps(message).encode())
                    username = True
                else:
                    user_text += event.unicode
                # it will set background color of screen

        if username == True:
            break
        SCREEN.fill((255, 255, 255))
        txt_surf = font.render("Please enter your username (Press Enter to submit) : ", True, font_color)
        SCREEN.blit(txt_surf, (100, 100))

        if active:
            color = color_active
        else:
            color = color_passive

            # draw rectangle and argument passed which should
        # be on screen
        pygame.draw.rect(SCREEN, color, input_rect)

        text_surface = font.render(user_text, True, (255, 255, 255))

        # render at position stated in arguments
        SCREEN.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))

        # set width of textfield so that text cannot get
        # outside of user's text input
        input_rect.w = max(100, text_surface.get_width() + 10)

        # display.flip() will update only a portion of the
        # screen to updated, not full area
        pygame.display.flip()

        # clock.tick(60) means that for every second at most
        # 60 frames should be passed.
        clock.tick(60)

    username = True
    return username

if __name__ == "__main__":
    start_client()