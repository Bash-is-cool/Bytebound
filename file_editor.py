import pygame
import time

class FileInterpreter:
    def __init__(self):
        pygame.init()
        pygame.key.set_repeat(400, 35)

        self.width = 700
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        pygame.display.set_caption("Code Editor & Interpreter")

        self.font = pygame.font.Font(None, 24)
        self.line_height = 25

        self.BG_COLOR = pygame.Color(20, 20, 25)
        self.TEXT_COLOR = pygame.Color(230, 230, 230)
        self.OUTPUT_COLOR = pygame.Color(100, 200, 255)
        self.CURSOR_COLOR = pygame.Color(255, 165, 0)
        self.DIVIDER_COLOR = pygame.Color(60, 60, 70)
        self.UI_TEXT_COLOR = pygame.Color(120, 120, 130)

        self.running = True

        self.file_lines = ["# Type code here...", "print Hello World", "add 5 10", "print Done!"]
        self.cursor_row = 3
        self.cursor_col = 11

        self.output_history = ["--- Interpreter Output [Press F5 to Run] ---"]

        self.cursor_visible = True
        self.last_cursor_toggle = time.time()
        self.cursor_interval = 0.5

    def interpret_code(self):
        self.output_history = ["--- Running Script ---"]
        variables = {}

        for line_num, raw_line in enumerate(self.file_lines):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            parts = line.split(" ", 1)
            command = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""

            if command == "print":
                self.output_history.append(f"[Out]: {args}")
            
            elif command == "add":
                try:
                    nums = [int(x) for x in args.split()]
                    self.output_history.append(f"[Out]: {sum(nums)}")
                except ValueError:
                    self.output_history.append(f"[Line {line_num+1} Error]: 'add' requires integers.")
            
            elif command == "clear":
                self.output_history = ["--- Output Cleared ---"]
            
            else:
                self.output_history.append(f"[Line {line_num+1} Error]: Unknown command '{command}'")

        self.output_history.append("--- Execution Finished ---")

    def handle_keydown(self, event):
        """Manages complex editing keys like Enter, Backspace, Arrows, and F5."""
        current_line = self.file_lines[self.cursor_row]

        if event.key == pygame.K_F5:
            self.interpret_code()

        elif event.key == pygame.K_RETURN:
            left_side = current_line[:self.cursor_col]
            right_side = current_line[self.cursor_col:]
            
            self.file_lines[self.cursor_row] = left_side
            self.file_lines.insert(self.cursor_row + 1, right_side)
            
            self.cursor_row += 1
            self.cursor_col = 0

        elif event.key == pygame.K_BACKSPACE:
            if self.cursor_col > 0:
                new_line = current_line[:self.cursor_col - 1] + current_line[self.cursor_col:]
                self.file_lines[self.cursor_row] = new_line
                self.cursor_col -= 1
                self.cursor_visible = True
            elif self.cursor_row > 0:
                prev_line = self.file_lines[self.cursor_row - 1]
                self.cursor_col = len(prev_line) 
                self.file_lines[self.cursor_row - 1] = prev_line + current_line
                self.file_lines.pop(self.cursor_row)
                self.cursor_row -= 1
                self.cursor_visible = True

        elif event.key == pygame.K_UP and self.cursor_row > 0:
            self.cursor_row -= 1
            self.cursor_col = min(self.cursor_col, len(self.file_lines[self.cursor_row]))
        elif event.key == pygame.K_DOWN and self.cursor_row < len(self.file_lines) - 1:
            self.cursor_row += 1
            self.cursor_col = min(self.cursor_col, len(self.file_lines[self.cursor_row]))
        elif event.key == pygame.K_LEFT:
            if self.cursor_col > 0:
                self.cursor_col -= 1
            elif self.cursor_row > 0: # Wrap to the previous line
                self.cursor_row -= 1
                self.cursor_col = len(self.file_lines[self.cursor_row])
        elif event.key == pygame.K_RIGHT:
            if self.cursor_col < len(current_line):
                self.cursor_col += 1
            elif self.cursor_row < len(self.file_lines) - 1: # Wrap to the next line
                self.cursor_row += 1
                self.cursor_col = 0

    def run(self):
        while self.running:
            self.screen.fill(self.BG_COLOR)
            current_time = time.time()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                elif event.type == pygame.TEXTINPUT:
                    current_line = self.file_lines[self.cursor_row]
                    new_line = current_line[:self.cursor_col] + event.text + current_line[self.cursor_col:]
                    self.file_lines[self.cursor_row] = new_line
                    self.cursor_col += len(event.text)

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    else:
                        self.handle_keydown(event)

            if current_time - self.last_cursor_toggle > self.cursor_interval:
                self.cursor_visible = not self.cursor_visible
                self.last_cursor_toggle = current_time

            editor_lbl = self.font.render("FILE EDITOR (script.txt)", True, self.UI_TEXT_COLOR)
            self.screen.blit(editor_lbl, (15, 10))
            
            start_y = 40
            for i, line in enumerate(self.file_lines):
                line_surface = self.font.render(line, True, self.TEXT_COLOR)
                self.screen.blit(line_surface, (30, start_y + (i * self.line_height)))

                if i == self.cursor_row and self.cursor_visible:
                    text_before_cursor = line[:self.cursor_col]
                    cursor_x_offset, _ = self.font.size(text_before_cursor)
                    cursor_x = 30 + cursor_x_offset
                    cursor_y = start_y + (i * self.line_height)
                    
                    pygame.draw.line(self.screen, self.CURSOR_COLOR, (cursor_x, cursor_y), (cursor_x, cursor_y + 18), 2)

            split_y = self.height // 2 + 50
            pygame.draw.line(self.screen, self.DIVIDER_COLOR, (0, split_y), (self.width, split_y), 3)
            
            output_lbl = self.font.render("CONSOLE INTERPRETER OUTPUT (Press F5 to execute)", True, self.UI_TEXT_COLOR)
            self.screen.blit(output_lbl, (15, split_y + 10))

            console_start_y = split_y + 45
            for j, out_line in enumerate(self.output_history):
                out_surface = self.font.render(out_line, True, self.OUTPUT_COLOR)
                self.screen.blit(out_surface, (30, console_start_y + (j * self.line_height)))

            pygame.display.update()

        pygame.quit()

if __name__ == "__main__":
    app = FileInterpreter()
    app.run()