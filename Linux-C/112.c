#include <stdio.h>

#define N 5
int a[N] = {3, 10, 1, 9, 5};


void insertion_sort(void)
{
    int i, j, k, temp;
    for(j = 1; j < N; j++){
        for(i = 0; i < N; i++)
            printf("%d  ", a[i]);
        temp = a[j];
        k = j-1;
        while(k >= 0 && a[k] > temp){
            a[k+1] = a[k];
            k--;
        }
        a[k+1] = temp;
    }
    for(i = 0; i < N; i++)
            printf("%d  ", a[i]);
}

int main(void)
{
    insertion_sort();
    return 0;
}