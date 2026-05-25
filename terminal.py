import pygame
import time

class Terminal:
    def __init__(self):
        pygame.init()

        self.width = 900
        self.height = 800
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Retro Terminal")

        self.font = pygame.font.Font(None, 28)
        
        self.BG_COLOR = pygame.Color(10, 10, 10)
        self.TEXT_COLOR = pygame.Color(50, 205, 50)
        
        self.running = True
        self.prompt = "> "
        self.user_text = ""
        
        self.history = ["Welcome to the Terminal.", "Type 'clear' to reset."]
        self.line_spacing = 30
        
        self.cursor_visible = True
        self.last_cursor_toggle = time.time()
        self.cursor_interval = 0.5

    def execute_command(self, command):
        """Process the command entered by the user."""
        cmd = command.strip().lower()
        if cmd == "clear":
            self.history.clear()
        elif cmd == "exit" or cmd == "quit":
            self.running = False
        elif cmd == "":
            pass
        else:
            self.history.append(f"Executed: {command}")

    def run(self):
        while self.running:
            self.screen.fill(self.BG_COLOR)
            current_time = time.time()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                elif event.type == pygame.TEXTINPUT:
                    self.user_text += event.text
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    
                    elif event.key == pygame.K_BACKSPACE:
                        self.user_text = self.user_text[:-1]
                        
                    elif event.key == pygame.K_RETURN:
                        self.history.append(self.prompt + self.user_text)
                        self.execute_command(self.user_text)
                        self.user_text = ""

            if current_time - self.last_cursor_toggle > self.cursor_interval:
                self.cursor_visible = not self.cursor_visible
                self.last_cursor_toggle = current_time

            current_y = self.height - 60 
            
            for line in reversed(self.history):
                if current_y < 10: # Stop drawing if we run off the top of the screen
                    break
                hist_surface = self.font.render(line, True, self.TEXT_COLOR)
                self.screen.blit(hist_surface, (15, current_y))
                current_y -= self.line_spacing

            input_y = self.height - 40
            full_input_string = self.prompt + self.user_text
            input_surface = self.font.render(full_input_string, True, self.TEXT_COLOR)
            self.screen.blit(input_surface, (15, input_y))

            if self.cursor_visible:
                text_width, _ = self.font.size(full_input_string)
                cursor_x = 15 + text_width
                
                pygame.draw.line(self.screen, self.TEXT_COLOR, (cursor_x, input_y), (cursor_x, input_y + 20), 2)
                
            pygame.display.update()

        pygame.quit()

if __name__ == "__main__":
    terminal = Terminal()
    terminal.run()