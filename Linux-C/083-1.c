# include <stdio.h>
# include <stdlib.h>
# include <time.h>
# define N 10000

int randon_array[N];

 void produce_random(int upper_bound)
{
     int i;
	 srand(time(NULL));
    for (i = 0; i < N; i++)
    {
        randon_array[i] = rand()% upper_bound;
    }
}

/* int howmany(int value)
{
    int count = 0, i;
    for (i = 0; i < N; i++)
    {
        if (randon_array[i] == value)
            ++count;
    }
    return count;
}*/

int main(void)
{
    int histogram[10] = {0}, i, j;
	produce_random(10);
	for (i = 0; i < N; i++)
		histogram[randon_array[i]]++;
    printf("Value\thowmany\n");
    for (j = 0; j < 10; j++)
        printf("%d\t%d\n", j, histogram[j]);
    return 0;
    
}