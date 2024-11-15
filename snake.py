import curses
import random
import os

# Path for the leaderboard file
LEADERBOARD_FILE = "snake_leaderboard.txt"

def load_leaderboard():
    """Load the leaderboard from a file."""
    if not os.path.exists(LEADERBOARD_FILE):
        return []
    with open(LEADERBOARD_FILE, "r") as file:
        scores = [line.strip() for line in file]
    return [int(score) for score in scores if score.isdigit()]

def save_score(score):
    """Save a new score to the leaderboard file."""
    scores = load_leaderboard()
    scores.append(score)
    scores = sorted(scores, reverse=True)[:5]  # Keep only top 5 scores
    with open(LEADERBOARD_FILE, "w") as file:
        for s in scores:
            file.write(f"{s}\n")

def get_score_color(score):
    """Get the color pair based on the score."""
    if score < 10:
        return curses.color_pair(4)
    elif score < 20:
        return curses.color_pair(5)
    elif score < 30:
        return curses.color_pair(6)
    elif score < 40:
        return curses.color_pair(7)
    else:
        return curses.color_pair(8)

def show_leaderboard(stdscr, scores):
    """Display the leaderboard."""
    stdscr.clear()
    sh, sw = stdscr.getmaxyx()
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Text color

    title = "Leaderboard"
    x_title = sw // 2 - len(title) // 2

    # Calculate the starting y position to center the content
    leaderboard_height = len(scores) + 5  # Number of score entries + spacing
    y_start = max(1, (sh - leaderboard_height) // 2)

    try:
        stdscr.addstr(y_start - 2, x_title, title, curses.A_BOLD | curses.color_pair(3))
    except curses.error:
        pass  # Ignore if the window is too small

    for i, score in enumerate(scores):
        rank_text = f"{i + 1}."
        score_text = f"{score}"
        x_rank = sw // 2 - len(rank_text + score_text + " ") // 2
        x_score = x_rank + len(rank_text) + 1

        # Get color based on score
        score_color = get_score_color(score)

        try:
            stdscr.addstr(y_start + i, x_rank, rank_text)
            stdscr.addstr(y_start + i, x_score, score_text, score_color)
        except curses.error:
            pass  # Ignore if the window is too small

    msg = "Press any key to continue"
    x_msg = sw // 2 - len(msg) // 2
    y_msg = y_start + len(scores) + 2

    try:
        stdscr.addstr(y_msg, x_msg, msg)
    except curses.error:
        pass  # Ignore if the window is too small

    stdscr.refresh()
    stdscr.getch()
    stdscr.clear()  # Clear the screen after showing leaderboard
    stdscr.refresh()

def main(stdscr):
    # Initialize the screen and colors
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()  # Use default terminal colors
    curses.init_pair(1, curses.COLOR_GREEN, -1)   # Initial snake color
    curses.init_pair(2, curses.COLOR_RED, -1)     # Food color
    curses.init_pair(3, curses.COLOR_YELLOW, -1)  # Text color

    # Additional color pairs for score display and snake gradient
    curses.init_pair(4, curses.COLOR_WHITE, -1)   # Score < 10
    curses.init_pair(5, curses.COLOR_CYAN, -1)    # Score 10-19
    curses.init_pair(6, curses.COLOR_GREEN, -1)   # Score 20-29
    curses.init_pair(7, curses.COLOR_YELLOW, -1)  # Score 30-39
    curses.init_pair(8, curses.COLOR_RED, -1)     # Score >= 40

    scores = load_leaderboard()
    game_running = True

    while game_running:
        # Show the leaderboard at the start
        show_leaderboard(stdscr, scores)

        # Initial snake setup
        stdscr.clear()
        stdscr.timeout(100)  # Set a delay for user input to control game speed
        sh, sw = stdscr.getmaxyx()
        snake = [
            [sh // 2, sw // 4],
            [sh // 2, sw // 4 - 1],
            [sh // 2, sw // 4 - 2]
        ]
        food = [sh // 2, sw // 2]
        try:
            stdscr.addch(food[0], food[1], curses.ACS_PI, curses.color_pair(2))
        except curses.error:
            pass  # Ignore errors if food position is invalid
        key = curses.KEY_RIGHT
        score = 0
        game_over = False

        direction = key  # Initial direction

        # Main game loop
        while not game_over:
            try:
                stdscr.addstr(0, 0, f'Score: {score}', curses.color_pair(3))
            except curses.error:
                pass  # Ignore if the window is too small

            stdscr.refresh()
            next_key = stdscr.getch()

            # Prevent reverse movement
            if next_key in [
                curses.KEY_UP,
                curses.KEY_DOWN,
                curses.KEY_LEFT,
                curses.KEY_RIGHT
            ]:
                opposite_directions = {
                    curses.KEY_UP: curses.KEY_DOWN,
                    curses.KEY_DOWN: curses.KEY_UP,
                    curses.KEY_LEFT: curses.KEY_RIGHT,
                    curses.KEY_RIGHT: curses.KEY_LEFT
                }
                if next_key != opposite_directions.get(direction):
                    direction = next_key

            key = direction

            # Calculate new head position
            y, x = snake[0]
            if key == curses.KEY_DOWN:
                y += 1
            elif key == curses.KEY_UP:
                y -= 1
            elif key == curses.KEY_LEFT:
                x -= 1
            elif key == curses.KEY_RIGHT:
                x += 1

            # Check for collision before updating the snake
            if (
                y < 0 or y >= sh or x < 0 or x >= sw or [y, x] in snake
            ):
                # Save and update leaderboard
                save_score(score)
                scores = load_leaderboard()

                # Display game over message
                stdscr.clear()
                sh, sw = stdscr.getmaxyx()

                # Prepare messages
                score_msg = f"You scored: {score}"
                msg1 = "Game Over!"
                msg2 = "Press 'q' to quit or any other key to restart."

                # Determine colors based on score
                score_color = get_score_color(score)

                # Make "Game Over!" bold
                game_over_attr = curses.A_BOLD | curses.color_pair(3)

                # Calculate positions
                y_center = sh // 2
                y_msg_score = y_center - 3
                y_msg1 = y_center - 1
                y_line = y_center
                y_msg2 = y_center + 1

                # Display messages
                try:
                    x_score = sw // 2 - len(score_msg) // 2
                    x_msg1 = sw // 2 - len(msg1) // 2
                    x_msg2 = sw // 2 - len(msg2) // 2

                    # Display score
                    stdscr.addstr(y_msg_score, x_score, score_msg, score_color)

                    # Display "Game Over!" in bold
                    stdscr.addstr(y_msg1, x_msg1, msg1, game_over_attr)

                    # Draw a line
                    stdscr.hline(y_line, 0, curses.ACS_HLINE, sw)

                    # Display "Press 'q'..." message
                    stdscr.addstr(y_msg2, x_msg2, msg2, curses.color_pair(3))
                except curses.error:
                    # If the window is too small, adjust the position
                    y_pos = 0
                    stdscr.addstr(y_pos, 0, score_msg, score_color)
                    y_pos += 1
                    stdscr.addstr(y_pos, 0, msg1, game_over_attr)
                    y_pos += 1
                    stdscr.addstr(y_pos, 0, msg2, curses.color_pair(3))

                stdscr.refresh()

                # Restart or quit option
                stdscr.nodelay(1)  # Set to non-blocking mode
                # Clear any pending inputs
                while stdscr.getch() != -1:
                    pass
                stdscr.nodelay(0)  # Set back to blocking mode
                choice = stdscr.getch()
                if choice == ord('q'):
                    game_running = False  # Exit the main loop to end the game
                    game_over = True
                else:
                    stdscr.clear()
                    game_over = True  # Break out of the game loop to restart

            else:
                # Update snake
                snake.insert(0, [y, x])

                # Check if snake has found the food
                if snake[0] == food:
                    score += 1
                    food = None
                    while food is None:
                        nf = [
                            random.randint(1, sh - 2),
                            random.randint(1, sw - 2)
                        ]
                        food = nf if nf not in snake else None
                    try:
                        stdscr.addch(
                            food[0],
                            food[1],
                            curses.ACS_PI,
                            curses.color_pair(2)
                        )
                    except curses.error:
                        pass  # Ignore errors if food position is invalid
                else:
                    # Move the snake by removing the last segment
                    tail = snake.pop()
                    try:
                        stdscr.addch(tail[0], tail[1], ' ')
                    except curses.error:
                        pass  # Ignore errors if tail position is invalid

                # Determine snake color based on score
                snake_color = get_score_color(score)

                # Draw snake head
                try:
                    stdscr.addch(
                        snake[0][0],
                        snake[0][1],
                        curses.ACS_CKBOARD,
                        snake_color
                    )
                except curses.error:
                    pass  # Ignore errors when drawing outside the window

curses.wrapper(main)
