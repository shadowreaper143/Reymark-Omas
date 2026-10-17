import pygame


class MobileButtons:

    def __init__(
        self,
        screen_width=800,
        screen_height=600
    ):

        button_width = 80
        button_height = 60

        bottom_y = (
            screen_height - 80
        )

        self.left = pygame.Rect(
            20,
            bottom_y,
            button_width,
            button_height
        )

        self.right = pygame.Rect(
            120,
            bottom_y,
            button_width,
            button_height
        )

        self.fire = pygame.Rect(
            screen_width - 120,
            bottom_y,
            100,
            button_height
        )

        self.control_color = (
            80,
            80,
            80
        )

        self.fire_color = (
            200,
            50,
            50
        )

        self.text_color = (
            255,
            255,
            255
        )

        self.font = pygame.font.SysFont(
            "Arial",
            22,
            bold=True
        )

    # =================================================
    # DRAW
    # =================================================

    def draw(
        self,
        screen
    ):

        pygame.draw.rect(
            screen,
            self.control_color,
            self.left,
            border_radius=10
        )

        pygame.draw.rect(
            screen,
            self.control_color,
            self.right,
            border_radius=10
        )

        pygame.draw.rect(
            screen,
            self.fire_color,
            self.fire,
            border_radius=10
        )

        left_text = self.font.render(
            "LEFT",
            True,
            self.text_color
        )

        right_text = self.font.render(
            "RIGHT",
            True,
            self.text_color
        )

        fire_text = self.font.render(
            "FIRE",
            True,
            self.text_color
        )

        screen.blit(
            left_text,
            (
                self.left.centerx
                - left_text.get_width() // 2,
                self.left.centery
                - left_text.get_height() // 2
            )
        )

        screen.blit(
            right_text,
            (
                self.right.centerx
                - right_text.get_width() // 2,
                self.right.centery
                - right_text.get_height() // 2
            )
        )

        screen.blit(
            fire_text,
            (
                self.fire.centerx
                - fire_text.get_width() // 2,
                self.fire.centery
                - fire_text.get_height() // 2
            )
        )

    # =================================================
    # HANDLE MOUSE
    # =================================================

    def handle_mouse(
        self,
        player,
        events
    ):

        mouse_pressed = pygame.mouse.get_pressed()

        if mouse_pressed[0]:

            mouse_pos = pygame.mouse.get_pos()

            if self.left.collidepoint(
                mouse_pos
            ):

                player.move_left()

            if self.right.collidepoint(
                mouse_pos
            ):

                player.move_right()

        for event in events:

            if (
                event.type
                == pygame.MOUSEBUTTONDOWN
                and event.button == 1
            ):

                if self.fire.collidepoint(
                    event.pos
                ):

                    return True

        return False