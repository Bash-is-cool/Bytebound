import pygame

class Terminal:
    pygame.init()

    width = 900
    height = 800
    running = True

    screen = pygame.display.set_mode((width, height))

    font = pygame.font.Font(None, 32)
    BOX_COLOR = pygame.Color("lightskyblue3")
    TEXT_COLOR = pygame.Color("white")

    input_rect = pygame.Rect(150, 150, 300, 40)
    user_text = "Type Here..."

    while running:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.TEXTINPUT:
                user_text += event.text
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_3 or event.key == pygame.K_ESCAPE:
                    running = False
                
                if event.key == pygame.K_BACKSPACE:
                    user_text = user_text[:-1]
                if event.key == pygame.K_RETURN:
                    user_text += "\n"
                
        text_surface = font.render(user_text, True, TEXT_COLOR)

        pygame.draw.rect(screen, BOX_COLOR, input_rect, 2)
        screen.blit(text_surface, (5, 5))
            
        pygame.display.update()

    pygame.quit()