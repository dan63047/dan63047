#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h> 

int main(){
    int a, b, sum, answer;
    bool error;
    error = false;
    while (!error)
    {
        a = rand() % 100;
        b = rand() % 100;
        sum = a + b;
        printf("%d + %d = ", a, b);
        scanf("%d", &answer);
        if (answer != sum){
            error = true;
        }
    }
    printf("LOX!!!\n");
    return 0;
}