# include <stdio.h>
# include <stdlib.h>
# define N 10000

int randon_array[N];

void produce_random(int upper_bound)
{
    int i;
	for (i = 0; i < N; i++)
    {
        randon_array[i] = random()% upper_bound;
    }
}

int howmany(int value)
{
    int count = 0, i;
    for (i = 0; i < N; i++)
    {
        if (randon_array[i] == value)
            ++count;
    }
    return count;
}

int main(void)
{
    int i;
	produce_random(10);
    printf("Value\thowmany\n");
    for (i = 0; i < 10; i++)
        printf("%d\t%d\n", i, howmany(i));
    return 0;
    
}