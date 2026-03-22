#include <stdio.h>

/* 4 направления: move
1 - право вверх
2 - право низ
3 - лево низ
4 - лево вверх
цикл while (пока кто то не наберет 21);
ввод -> ракетки; движение мячика;
racket1 = верхняя точка левой ракетки (первой)
racket2 = верхняя точка правой ракетки (второй)
может быть понадобиться while (getchar() != '\n'); // очистка буфера
*/

int correct_input() {
    int flag = 0;
    char c;
    scanf("%c", &c);
    if (c == 'A' || c == 'a') {
        flag = 1;  // если нажали а или А позиция ракетки 1 игрока вверх (-1)
    }
    if (c == 'Z' || c == 'z') {
        flag = 2;  // если нажали z или Z позиция ракетки 1 игррока вниз (+1)
    }
    if (c == 'k' || c == 'K') {
        flag = 3;  // если нажали k или K позиция ракетки 2 игрока вверх (-1)
    }
    if (c == 'm' || c == 'M') {
        flag = 4;  // если нажали m или M позиция ракетки 2 игрока вниз (+1)
    }
    if (c == ' ') {
        flag = 5;
    }
    return flag;  // если флаг 0, то мы ниче не делаем
}

int racket_pos1(int flag, int racket1) {  // движение первой ракетки ( левой )
    switch (flag) {
        case 1:
            if (racket1 > 1) {
                racket1--;
            }  //(y первой ракетки)
            break;
        case 2:
            if (racket1 < 21) {
                racket1++;
            }  //(y первой ракетки)
            break;
    }
    return racket1;
}
int racket_pos2(int flag, int racket2) {  // движение второй ракетки (правой)
    switch (flag) {
        case 3:
            if (racket2 > 1) {
                racket2--;
            }  //(y второй ракетки)
            break;
        case 4:
            if (racket2 < 21) {
                racket2++;
            }  //(y второй ракетки)
            break;
    }
    return racket2;
}

int check_wall(int move, int ball_y) {  // изменение направления, при столкновении мячика со стенками
    if (ball_y <= 1) {
        if (move == 1) {
            move = 2;
        } else if (move == 4) {
            move = 3;
        }
    }
    if (ball_y >= 23) {
        if (move == 2) {
            move = 1;
        } else if (move == 3) {
            move = 4;
        }
    }
    return move;
}

int check_racket1(int racket1, int move, int ball_y,
                  int ball_x) {  // изменение направление мяча, при отбивании
                                 // первой ракеткой (левой)
    if (ball_x == 2 && ball_y >= racket1 - 1 &&
        ball_y <= racket1 + 3) {  // может быть тут ball_x = 2 если 1 поле занимают границы
        if (move == 3) move = 2;
        if (move == 4) move = 1;
    }
    return move;
}
int check_racket2(int racket2, int move, int ball_y, int ball_x) {
    if (ball_x == 77 && ball_y >= racket2 - 1 && ball_y <= racket2 + 3) {
        if (move == 2) move = 3;
        if (move == 1) move = 4;
    }
    return move;
}
int ball_new_x(int move,
               int ball_x) {  // тернарник сделал, можно сделать проще, через
                              // обычный if; это изменение координаты по оси x
                              // которое зависит от направления
    return (move == 1 || move == 2) ? ball_x + 1 : ball_x - 1;
}
int ball_new_y(int move,
               int ball_y) {  // тернарник сделал, можно сделать проще, через
                              // обычный if; это изменение координаты по оси y
                              // которое зависит от направления
    return (move == 1 || move == 4) ? ball_y - 1 : ball_y + 1;
}

// Отрисовка поля
void draw_field(int width, int height, int y_first, int y_second, int x_ball, int y_ball, int score1,
                int score2) {
    printf("\033[2J\033[H");  // очистка терминала перед каждой итерацией отрисовки
    for (int i = 0; i < height; ++i) {  // цикл по i отвечает за y, по j за x
        for (int j = 0; j < width; ++j) {
            if (i == 0 || i == 24) {  // отрисовка верхней и нижней грани + перенос каретки в конце
                printf("#");
                if (j == 79) {
                    printf("\n");
                }
            } else if ((j == 0 || j == 79) && (i != 0 || i != 24)) {  // отрисовка правой и левой
                if (j == 79) {
                    printf("|\n");
                } else {
                    printf("|");
                }
            } else if (i == y_ball && j == x_ball) {  // отрисовка мяча (перекрывает собой символы центра)
                printf("0");
            } else if ((j == 39 || j == 40) && (i != 0 || i != 79)) {  // отрисовка центра
                printf("|");
            } else if ((i == y_first || i == (y_first + 1) || i == (y_first + 2)) &&
                       j == 1) {  // отрисовка левой ракетки
                printf("]");
            } else if ((i == y_second || i == (y_second + 1) || i == (y_second + 2)) &&
                       j == 78) {  // отрисовка правой ракетки
                printf("[");
            } else {  // заполнение пробелами
                printf(" ");
                if (j == 79) {
                    printf("\n");
                }
            }
        }
    }
    if (score1 == 21)
        printf("\n🎉 Left player WIN! Score %d:%d\n", score1, score2);
    else if (score2 == 21)
        printf("\n🎉 Right player WIN! Score %d:%d\n", score2, score1);
    else
        printf("Score: Left player [%d]  |  Right player [%d]\n", score1, score2);
}

int main() {
    int width = 80;
    int height = 25;
    int y_first = 2;
    int y_second = 20;
    int x_ball = 42;
    int y_ball = 13;
    int score1 = 0, score2 = 0;
    draw_field(width, height, y_first, y_second, x_ball, y_ball, score1, score2);
    int move = 1;  // направление мяча

    while (score1 < 21 && score2 < 21) {
        int flag = 0;
        while (flag == 0) {
            flag = correct_input();
        }

        y_first = racket_pos1(flag, y_first);
        y_second = racket_pos2(flag, y_second);

        if (flag >= 1 && flag <= 5) {
            move = check_wall(move, y_ball);
            move = check_racket1(y_first, move, y_ball, x_ball);
            move = check_racket2(y_second, move, y_ball, x_ball);
            x_ball = ball_new_x(move, x_ball);
            y_ball = ball_new_y(move, y_ball);
        }

        if (x_ball <= 0) {
            score2++;
            x_ball = width / 2;
            y_ball = height / 2;
            move = 1;
        } else if (x_ball >= width - 1) {
            score1++;
            x_ball = width / 2;
            y_ball = height / 2;
            move = 3;
        }
        draw_field(width, height, y_first, y_second, x_ball, y_ball, score1, score2);
    }
    return 0;
}
