#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <signal.h>
#define __USE_GNU
#include <sched.h>
#include <sys/mman.h>
#include <getopt.h>
#include <pthread.h>
#include <signal.h>
#include <errno.h>
#include <sys/types.h>
#include <linux/unistd.h>

#include <sched_gsched.h>
#include <ccsm.h>

#define NUMBER_OF_THREADS 4
#define gettid() syscall(__NR_gettid)

static int pipeline_len;
int ccsm_fd;
int grp_fd;

#define help_string "\
\n\nusage %s --threads=<int> [--without-rt] [--help]\n\n\
\t--threads=\tnumber of threads in pipeline\n\
\t--help\t\tthis menu\n\n"

void display_help(char **argv)
{
	printf(help_string, argv[0]);
}

/*
 * This simple example exists to illustrate one of the redezvous situations.
 * In this case, all of the threads announce themselves via CCSM before
 * attempting to register themselves with GS.
 *
 * The simplest possible variation is to simply have threads randomly register before
 * and after they announce themselves.
 *
 */

/* process command line options */
void process_options (int argc, char *argv[])
{
	int error = 0;
	
	for (;;) {
		int option_index = 0;

		static struct option long_options[] = {
			{"threads",          required_argument, NULL, 't'},
			{"help",             no_argument,       NULL, 'h'},
			{NULL, 0, NULL, 0}
		};

		/*
		 * c contains the 4th element in the lists above corresponding to
		 * the long argument the user used.
		 */
		int c = getopt_long(argc, argv, "int:c:", long_options, &option_index);

		if (c == -1)
			break;
		switch (c) {
		case 0:
			switch (option_index) {
			case 0:
				display_help(argv);
				exit(0);
				break;
			}
			break;

		case 't':
			pipeline_len = atoi(optarg);
			break;

		case 'h':
			error = 1;
			break;
		}				
	}

	if (pipeline_len <= 0) {
		printf("\nerror: pipeline length must be > 0");
		error = 1;
	}

	if (error) {
		display_help(argv);
		exit(1);
	}
}

void *thread_function_run(void *arg){
	char name[12];
	int id = (int)arg;

	memset(name, 0, sizeof(name));
	sprintf(name, "thread-%d", id);
	printf("Registering task with ccsm name:%s\n", name);

	ccsm_create_component_self(ccsm_fd, name);
	grp_name_join_group(grp_fd, "main", name, 0);

	/******BODY******/
	/*
	 * This is the body of the code. To make a more complicated example we might
	 * consider expanding this with more random actions and / or periods of
	 * action interrupted with periods of sleep.
	 */
	sleep(5);
	/******BODY******/
	
	return NULL;
}

int main(int argc, char **argv){
	pthread_t *threads;
	int i=0;
	void *ret;
	
	process_options(argc, argv);
	
	grp_fd = grp_open();
	if (grp_fd < 0) {
		perror("grp_fd");
		return 1;
	}

	ccsm_fd = ccsm_open();
	if (ccsm_fd < 0) {
		perror("ccsm_fd");
		return 1;
	}

	grp_create_group(grp_fd, "main", "sdf_seq");
	gsched_install_group(grp_fd, "main", "main_member");
			
	threads = malloc(sizeof(pthread_t) * pipeline_len);
	if (!threads){
		fprintf(stderr, "can't initialise threads\n");
		exit(1);
	}

	printf("Creating the required set of threads.....\n");
	for(i=0;i<pipeline_len;i++){
		if (pthread_create(&threads[i],NULL,&thread_function_run, (void *)i)){
		       	fprintf(stderr, "failed creating thread");
        		exit(1);
        	}
	}
	
	for(i=0;i<pipeline_len;i++){
		pthread_join(threads[i], &ret);
	}

	gsched_uninstall_group(grp_fd, "main_member");
	grp_destroy_group(grp_fd, "main");
	ccsm_close(ccsm_fd);
	grp_close(grp_fd);

	return 0;
}

