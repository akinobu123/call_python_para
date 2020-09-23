#include<stdio.h>
#include<stdlib.h>

int main(void)
{
	printf("c start\n");
	system("python task_broker.py --task_name draw-contour --task_param ../img/apple.jpg,../img/apple_out.jpg");
	printf("c end\n");
	return 0;
}
