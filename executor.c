#include<stdio.h>
#include<stdlib.h>

int main(void)
{
	printf("c start\n");
	system("python task_broker.py --task_name aaa --task_param test");
	printf("c end\n");
	return 0;
}
