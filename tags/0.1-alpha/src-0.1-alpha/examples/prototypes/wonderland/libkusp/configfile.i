 /* configfile.i 
 *
 * SWIG Interface file for configfile.c.
 * Replaces configfilemodule.c
 * 
 */
 %module configfilemod
 %{
extern valuetype_t value_type(value_t *val)
extern long as_long_long(value_t *v) 
extern char *as_string(value_t *v) 
extern struct hashtable *as_hashtable(value_t *v) 
extern list_t *as_list(value_t *v) 
extern int as_bool(value_t *v) 
extern int as_int(value_t *v) 
extern value_t *encap_long(long long value) 
extern value_t *encap_int(int value) 
extern value_t *encap_double(double value) 
extern value_t *encap_string_ptr(char *value) 
extern value_t *encap_string(char *value) 
extern value_t *encap_reference(char *value) 
extern value_t *encap_hash(hashtable_t *hash) 
extern value_t *encap_invoc(invocation_t *invoc) 
extern value_t *encap_list(list_t *list) 
extern valuetype_t listitem_type(list_t *list) 
extern hashtable_t *create_dictionary() 
extern void free_config(hashtable_t *config)  
extern void free_value(value_t *value) 
extern static hashtable_t *copy_dictionary(hashtable_t *d)
extern value_t *copy_value(value_t *v)
extern static void fix_dict_toplevel(hashtable_t *d, hashtable_t *toplevel)
extern void fix_toplevel(value_t *v, hashtable_t *toplevel)
extern static void strip_dict_context(hashtable_t *d)
extern void strip_context_lists(value_t *v)
extern value_t *follow(value_t *v)
extern int unhash_int(hashtable_t *h, char *key, int *val)
extern int unhash_bool(hashtable_t *h, char *key, int *val)
extern int unhash_long(hashtable_t *h, char *key, long long *val)
extern int unhash_double(hashtable_t *h, char *key, double *val)
extern int unhash_string(hashtable_t *h, char *key, char **val)
extern int unhash_hashtable(hashtable_t *h, char *key, hashtable_t **val)
extern int unhash_list(hashtable_t *h, char *key, list_t **val)
extern int unhash_invoc(hashtable_t *h, char *key, invocation_t **val) 
extern valuetype_t hashtable_get_type(hashtable_t *h, char *key)
extern int unlist_invoc(list_t *list, invocation_t **val)
extern int unlist_int(list_t *list, int *val)
extern int unlist_bool(list_t *list, int *val)
extern int unlist_long(list_t *list, long long *val)
extern int unlist_double(list_t *list, double *val)
extern int unlist_string(list_t *list, char **val)
extern int unlist_hashtable(list_t *list, hashtable_t **val)
extern int unlist_list(list_t *list, list_t **val)
extern static int __print_value(FILE *fd, value_t *value, int indent) 
extern void write_value(FILE *fd, value_t *value) 
extern void prettyprint_value(value_t *value) 
extern void prettyprint_hash(hashtable_t *hash) 
extern void prettyprint_list(list_t *list) 
extern int valcmp(const value_t *v1, const value_t *v2)
extern int list_membership_test(list_t *head, const value_t *v)
extern int string_inside_list(list_t *head, char *string)
extern int write_config(FILE *fd, hashtable_t *config) 
extern void config_to_string(hashtable_t *config, size_t *size, char **ptr)
extern hashtable_t *parse_config(char *filename) 
extern hashtable_t *parse_config_string(char *config) 
extern char *get_type_name(valuetype_t v) 
%}

extern valuetype_t value_type(value_t *val)
extern long as_long_long(value_t *v) 
extern char *as_string(value_t *v) 
extern struct hashtable *as_hashtable(value_t *v) 
extern list_t *as_list(value_t *v) 
extern int as_bool(value_t *v) 
extern int as_int(value_t *v) 
extern value_t *encap_long(long long value) 
extern value_t *encap_int(int value) 
extern value_t *encap_double(double value) 
extern value_t *encap_string_ptr(char *value) 
extern value_t *encap_string(char *value) 
extern value_t *encap_reference(char *value) 
extern value_t *encap_hash(hashtable_t *hash) 
extern value_t *encap_invoc(invocation_t *invoc) 
extern value_t *encap_list(list_t *list) 
extern valuetype_t listitem_type(list_t *list) 
extern hashtable_t *create_dictionary() 
extern void free_config(hashtable_t *config)  
extern void free_value(value_t *value) 
extern static hashtable_t *copy_dictionary(hashtable_t *d)
extern value_t *copy_value(value_t *v)
extern static void fix_dict_toplevel(hashtable_t *d, hashtable_t *toplevel)
extern void fix_toplevel(value_t *v, hashtable_t *toplevel)
extern static void strip_dict_context(hashtable_t *d)
extern void strip_context_lists(value_t *v)
extern value_t *follow(value_t *v)
extern int unhash_int(hashtable_t *h, char *key, int *val)
extern int unhash_bool(hashtable_t *h, char *key, int *val)
extern int unhash_long(hashtable_t *h, char *key, long long *val)
extern int unhash_double(hashtable_t *h, char *key, double *val)
extern int unhash_string(hashtable_t *h, char *key, char **val)
extern int unhash_hashtable(hashtable_t *h, char *key, hashtable_t **val)
extern int unhash_list(hashtable_t *h, char *key, list_t **val)
extern int unhash_invoc(hashtable_t *h, char *key, invocation_t **val) 
extern valuetype_t hashtable_get_type(hashtable_t *h, char *key)
extern int unlist_invoc(list_t *list, invocation_t **val)
extern int unlist_int(list_t *list, int *val)
extern int unlist_bool(list_t *list, int *val)
extern int unlist_long(list_t *list, long long *val)
extern int unlist_double(list_t *list, double *val)
extern int unlist_string(list_t *list, char **val)
extern int unlist_hashtable(list_t *list, hashtable_t **val)
extern int unlist_list(list_t *list, list_t **val)
extern static int __print_value(FILE *fd, value_t *value, int indent) 
extern void write_value(FILE *fd, value_t *value) 
extern void prettyprint_value(value_t *value) 
extern void prettyprint_hash(hashtable_t *hash) 
extern void prettyprint_list(list_t *list) 
extern int valcmp(const value_t *v1, const value_t *v2)
extern int list_membership_test(list_t *head, const value_t *v)
extern int string_inside_list(list_t *head, char *string)
extern int write_config(FILE *fd, hashtable_t *config) 
extern void config_to_string(hashtable_t *config, size_t *size, char **ptr)
extern hashtable_t *parse_config(char *filename) 
extern hashtable_t *parse_config_string(char *config) 
extern char *get_type_name(valuetype_t v) 