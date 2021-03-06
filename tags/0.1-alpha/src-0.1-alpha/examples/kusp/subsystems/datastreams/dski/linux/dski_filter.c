#include <asm/uaccess.h>
#include <linux/limits.h>
#include <linux/sched.h>
#include <linux/file.h>
#include <linux/kernel.h>
#include <linux/list.h>
#ifdef CONFIG_TASK_ALIAS
#include <linux/taskalias.h>
#endif
#ifdef CONFIG_GROUPSCHED
#include <linux/sched_gsched.h>
#endif
#include <linux/dski.h>
#ifdef CONFIG_DISCOVERY
#include <linux/dscvr.h>
#include <linux/dski_netdata.h>
#include <linux/mount.h>
#include <linux/dcache.h>
#endif

#include <datastreams/dski.h>
#include "dski_common.h"

/*
 * TODO: This code could use some work
 */

/*
 * -- Event Filtering Framework --
 *
 * -- Filtering Functions --
 *
 * Each filter must define a set of functions which implement the filter's
 * logic. These are 1) the main filtering function, 2) filter configuration
 * function, and 3) the filter clean up function.
 *
 * Only the first function, the filtering function, is required. Below are the
 * declarations of these functions and a description of their parameters
 */

/*
 * filter_f_func - filter decision function
 *
 * @datastream:		- associated datastream
 * @event record:	- event to filter (accept or reject)
 * @void*:		- private filter specific data
 */
typedef int filter_f_func(struct datastream *, 
		struct ds_event_record *, void *,int data_len,const void *dat);

/*
 * filter_c_func - filter configuration function
 *
 * @datastream:		- associated datastream
 * @void**:		- ptr to filter's private data pointer
 * @void*:		- ptr to configuration data
 * @size_t:		- size of configuration data
 */
typedef int filter_c_func(struct datastream *, void **,
		union dski_ioc_filter_ctrl_params *);

/*
 * filter_d_func - filter cleanup function
 *
 * @datastream:		- associated datastream
 * @void*:		- ptr to filter's private data
 */
typedef void filter_d_func(struct datastream *, void *);


/*
 * struct filter_decl - declaration of a specific filter type
 *
 * One of these exists for each filter type and is listed in the filters[]
 * array. Users of a particular filter allocate a struct active_filter which
 * contains a pointer to the specific filter, and private filter data.
 */
struct filter_decl {
	char *name;			/* name of filter */
	filter_f_func *filt_func;	/* called to perform filtering */
	filter_c_func *conf_func;	/* called to configure filter */
	filter_d_func *dest_func;	/* called to cleanup filter */
};

/*
 * struct active_filter - one instance of a particular filter type
 */
struct active_filter {
	struct list_head list;			/* on list of per-datastream filters */
	const struct filter_decl *filter;	/* specific filter */
	void *data;				/* private data */
};




/******** FLIGHT RECORDER FILTER (IDEA) ******/

/*
 * Flight Recorder Filter:
 * 	Assuming that Relay-FS permits specificy a circular buffer area in which
 * 	events will be logged and continuously wrap around in the specficed
 * 	buffers, then creating a Flight Recorder mode is relatively simple using
 * 	an Active Filter. The Active Filter will examine the stream of events
 * 	and retain any state information required to evaluate when the recording
 * 	capture action should be taken. When the recording capture condition is
 * 	satisfied, the Active Filter causes the circular Relay-FS buffer to be
 * 	released to the user and a new circular buffer area to be used.
 */





/******* PID FILTER ***********/

struct pidfilter_priv_elem {
	long pid;
	int match_response;
#ifdef CONFIG_TASK_ALIAS
	alias_t alias;
#endif
};

struct pidfilter_priv {
	struct pidfilter_priv_elem *pids;
	int size;
	int default_response;
};

/*
 * This is invoked for every event enabled for this datastream and checks
 * whether this event should be accepted or rejected.
 */
int pidfilter_f_func(struct datastream *d, struct ds_event_record *evt, 
		void *data,int data_len,const void *dat)
{
	struct pidfilter_priv *priv = data;
	int i;

	/*
	 * This loop iterates through the set of process related filtering
	 * operations which can specify either a task alias name or a PID and
	 * associate a response with each. For example, we might associate PID
	 * 1234 with a REJECT response. In another case, we might associate the
	 * name "Fred" with a set of threads under task alias and specify here
	 * that any event generated by a member of the set "Fred" should be
	 * accepted.
	 */
	for (i = 0; i < priv->size; i++) {
#ifdef CONFIG_TASK_ALIAS
		if (priv->pids[i].pid == -1) {
			if (task_alias_exists_quick(current, priv->pids[i].alias)) {
				return priv->pids[i].match_response;
			}
			continue;
		} 
#endif
		if (current->pid == priv->pids[i].pid){
			return priv->pids[i].match_response;
		}

	}

	return priv->default_response;
}

/*
 * Destructor for this filter.
 */
void pidfilter_d_func(struct datastream *d, void *data)
{
	struct pidfilter_priv *filterdata = data;
	int i;

#ifdef CONFIG_TASK_ALIAS
	/* 
	 * For every per-process filter specification, check if was using a task
	 * alias key and if so release this filter's reference to it, which was
	 * obtained in the constructor function.
	 */
	for (i=0; i < filterdata->size; i++) {
		if (filterdata->pids[i].pid != -1) {
			continue;
		}

		task_alias_put_alias_handle(filterdata->pids[i].alias);
	}
#endif
	/* Free data allocated in the constructor */
	kfree(filterdata->pids);
	kfree(filterdata);
}

/*
 * Constructor of the per-process filter. Note that this filter can use either
 * PID number or an abstract set name (if Task Alias is configured) as the key
 * for deciding what to do.
 */
int pidfilter_c_func(struct datastream *d, void **data, 
		union dski_ioc_filter_ctrl_params *params)
{
	struct dski_pid_filter_elem *upids, *upidsptr;
	struct pidfilter_priv_elem *elements;
	size_t size = params->pidfilter.pid_array_size;
	struct pidfilter_priv *priv;
	int i, numpids;

	/* User-space ptr to the list of process keys */
	upidsptr = params->pidfilter.pids;
	if (!upidsptr || !size)
		return -EINVAL;

	/* Pointer to kernel space for our copy of process keys */
	upids = kmalloc(size, GFP_KERNEL);
	if (!upids)
		return -ENOMEM;

	/* Pointer to the filter's private data which is configured here */
	priv = kmalloc(sizeof(*priv), GFP_KERNEL);
	if (!priv) {
		kfree(upids);
		return -ENOMEM;
	}

	/* Copy the list of keys from user space to kernel space */
	if (copy_from_user(upids, upidsptr, size)) {
		kfree(upids);
		kfree(priv);
		return -EFAULT;
	}


	/*
	 * Create private filter data which can hold the list of process key
	 * information in the format most appropriate for use during logging.
	 */
	numpids = size / sizeof(*upids);
	elements = kmalloc(sizeof(*elements) * numpids, GFP_KERNEL);
	if (!priv) {
		kfree(upids);
		kfree(priv);
		return -ENOMEM;
	}

	/*
	 * For each process key, establish a usable set of information.
	 */
	for (i = 0; i < numpids; i++) {
		if (strlen(upids[i].name) != 0) {
#ifdef CONFIG_TASK_ALIAS
			/*
			 * Obtain a reference to a named set in Task Alias and
			 * create it if it does not already exist. Note that if
			 * this statement creates it, it has no members, and
			 * will not affect filter action until some tasks join
			 * the set.
			 */
			if (task_alias_get_alias_handle_always(upids[i].name, 
						&elements[i].alias)) {
				kfree(upids);
				kfree(priv);
				kfree(elements);
				printk(KERN_CRIT "dski: task_alias_get_alias_handle failed\n");
				return -ENOMEM;
			}
			/* If we are using a TA name, we note this a PID -1 */
			elements[i].pid = -1;
#else
			/*
			 * Obviously an error to specify a name if TA not
			 * available
			 */
			printk(KERN_CRIT "Tried to filter on name using non-taskalias kernel\n");
			kfree(upids);
			kfree(priv);
			kfree(elements);
			return -EINVAL;
#endif
		} else {
			/* Specified no name and so use PID */
			elements[i].pid = upids[i].pid;
		}
		/* Store specified response which can be ACCEPT, REJECT, PASS */
		elements[i].match_response = upids[i].match_response;
	}
	kfree(upids);

	/* Finish filling in the private data for the filter */
	priv->size = numpids;
	priv->pids = elements;
	priv->default_response = params->pidfilter.default_response;
	*data = priv;
	return 0;
}

/*
 * filters[] - list of a available filters
 *
 * FIXME: replace with some kind of hash table, to allow for other
 * filter modules
 */
static const struct filter_decl filters[] = {
	{FLTR_PID, pidfilter_f_func, pidfilter_c_func, pidfilter_d_func},
#ifdef CONFIG_DISCOVERY
//	{FLTR_DSCVR, dscvr_filter_f_func, dscvr_filter_c_func, dscvr_filter_d_func},
// system Monitor functions.
//	{FLTR_SMONITOR, smonitor_f_func, smonitor_c_func, smonitor_d_func},
#endif
//	{FLTR_DTRACE, dtrace_f_func, dtrace_c_func, dtrace_d_func},

	{FLTR_TASK, taskfilter_f_func, taskfilter_c_func, taskfilter_d_func},
	
	{FLTR_CCSM_TRACEME, traceme_f_func, traceme_c_func, traceme_d_func},

	{NULL}
};

int apply_filters(struct datastream *d, struct ds_event_record *evt, int data_len, const void *dat)
{
	struct active_filter *filter_instance;
	int ret;

	rcu_read_lock();

	list_for_each_entry_rcu(filter_instance, &d->filters, list) {
		
		BUG_ON(!filter_instance->filter->filt_func);
		ret = filter_instance->filter->filt_func(d, evt, filter_instance->data, data_len, dat);
		
		switch (ret) {
		case FLTR_REJECT: 
			/* FIXME.b //DSKI_FILTER_REJECT:
			 *
			 * The current filter has rejected the event and it will
			 * not be logged.
			 */
			rcu_read_unlock();
			return FLTR_REJECT;
		case FLTR_PASS: 
			/* FIXME.b //DSKI_FILTER_PASS:
			 *
			 * The current filter has not rejected the event but
			 * the event should be considered by any further filters
			 * in the pipeline.
			 */
			continue;
		case FLTR_ACCEPT: 
			/*FIXME.b//DSKI_FILTER_LOG_IMMEDIATE:
			 *
			 * The current filter has decided the event should be
			 * logged immediately, skipping further filtering.
			 */
			rcu_read_unlock();
			return FLTR_ACCEPT;
		default:
			WARN_ON(1);
		}
	}

	rcu_read_unlock();

	return 0;
}

/*
 * create_filter - create and initialize a filter
 *
 * The filter is added to the end of the list of filters which are applied to
 * the specified datastream. Once the routine returns the filter has been
 * configured and is live
 */
int create_filter(struct dstrm_user *user, char *dstrm, char *name,
		union dski_ioc_filter_ctrl_params *params)
{
	const struct filter_decl *fd;
	struct active_filter *filter_instance;
	struct datastream *d;
	int ret;

	d = find_datastream(user, dstrm);
	if (!d)
		return -EINVAL;

	fd = &filters[0];
	while (fd->name) {
		if (strcmp(fd->name, name) == 0)
			break;
		fd++;
	}

	if (!fd->name)
		return -EINVAL;

	filter_instance = kmalloc(sizeof(struct active_filter), GFP_KERNEL);
	if (!filter_instance)
		return -ENOMEM;

	if (fd->conf_func) {
		ret = fd->conf_func(d, &filter_instance->data, params);
		if (ret) {
			kfree(filter_instance);
			return ret;
		}
	}

	filter_instance->filter = fd;
	list_add_tail_rcu(&filter_instance->list, &d->filters);

	return 0;
}

/*
 * destroy_filters - remove all filters from a datastream
 */
int destroy_filters(struct datastream *d)
{
	struct list_head head;
	struct active_filter *filter_instance, *tmp;

	if (list_empty(&d->filters))
		return 0;

	head = d->filters;
	INIT_LIST_HEAD(&d->filters);
	head.prev->next = &head;
	head.next->prev = &head;
	synchronize_rcu();

	list_for_each_entry_safe(filter_instance, tmp, &head, list) {
		if (filter_instance->filter->dest_func)
			filter_instance->filter->dest_func(d, filter_instance->data);
		list_del(&filter_instance->list);
		kfree(filter_instance);
	}

	return 0;
}
