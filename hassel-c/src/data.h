#ifndef _DATA_H_
#define _DATA_H_

#include "array.h"
#include "parse.h"

struct PACKED file {
  uint32_t arrs_ofs, strs_ofs;
  uint32_t ntfs, stages;
  uint32_t tf_ofs[0];
};

#define VALID_OFS 1

extern struct file *data_file;
extern uint8_t     *data_raw;
extern size_t       data_size;

#define DATA_ARR(X) ( data_arrs + ((X) - VALID_OFS) / sizeof (array_t) )
#define DATA_STR(X) ( data_strs + ((X) - VALID_OFS) )

extern array_t *data_arrs;
extern uint32_t data_arrs_len, data_arrs_n;
extern char    *data_strs;

void data_load   (const char *);
void data_unload (void);

void data_gen (const char *, const struct parse_ntf *, const struct parse_tf *);

#endif

