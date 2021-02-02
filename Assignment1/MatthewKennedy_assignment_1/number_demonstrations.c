#include <stdio.h>

int main(int argc, char** argv)
{
	//Problem 1
	float a = 2.5;
	printf("Problem 1: %.10f\n", a);

	//Problem 2
	float b = -1.0/10.0;
	printf("Problem 2: %.10f\n", b);

	//Problem 3
	double c;
	c = 1/3;
	printf("Problem 3.1: %.10f\n", c);
	c = 1.0/3.0;
	printf("Problem 3.2: %.10f\n", c);

	//Problem 4
	double d;
	d = 9999999.3399999999;
	printf("Problem 4.1: %.10f\n", d);
	d = (float) d;
	printf("Problem 4.2: %.10f\n", d);

	//Problem 5
	int e = 30000*30000;
	printf("Problem 5.1: %d\n", e);
	e = 40000*40000;
	printf("Problem 5.2: %d\n", e);
	e = 50000*50000;
	printf("Problem 5.3: %d\n", e);
	e = 60000*60000;
	printf("Problem 5.4: %d\n", e);
	e = 70000*70000;
	printf("Problem 5.5: %d\n", e);

	//Problem 6
	float h = 1e20;
	printf("Problem 6.1: %f\n", h);
	float i = (1e20 + 3500000000);
	printf("Problem 6.2: %f\n", i);
	float j = (1e20 + (3500000000 * 1000000000));
	printf("Problem 6.3: %f\n", j);
	float k = 1e20;
	for (int i = 0; i < 1000000000; i++)
		k += 3500000000;
	printf("Problem 6.4: %f\n", k);

}
