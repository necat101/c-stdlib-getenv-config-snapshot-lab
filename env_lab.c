#define _DEFAULT_SOURCE
#define _POSIX_C_SOURCE 200809L
#define _XOPEN_SOURCE 700
#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <limits.h>
#include <errno.h>
#include <stdio.h>
#include <unistd.h>

#ifndef CHAR_BIT
#define CHAR_BIT 8
#endif

static void json_str(const char *s) {
    putchar('"');
    if (!s) { putchar('"'); return; }
    for (; *s; s++) {
        unsigned char c = (unsigned char)*s;
        if (c == '"' || c == '\\') { putchar('\\'); putchar(c); }
        else if (c == '\n') { fputs("\\n", stdout); }
        else if (c == '\r') { fputs("\\r", stdout); }
        else if (c < 32) { printf("\\u%04x", c); }
        else putchar(c);
    }
    putchar('"');
}

/* bounded getenv copy helper */
static int getenv_bounded_copy(const char *name, char *out, size_t out_cap, size_t *required_out) {
    if (!out || !required_out) return -1;
    char *p = getenv(name);
    if (!p) { *required_out = 0; return 1; } /* missing */
    size_t len = strlen(p);
    size_t req = len + 1;
    *required_out = req;
    if (out_cap < req) return 2; /* insufficient */
    memcpy(out, p, req);
    return 0;
}

int main(void) {
    printf("{\n");
    printf("  \"stashed\": {\n");
#ifdef __STDC_VERSION__
    printf("    \"STDC_VERSION\": %ld,\n", (long)__STDC_VERSION__);
#else
    printf("    \"STDC_VERSION\": null,\n");
#endif
    printf("    \"CHAR_BIT\": %d,\n", CHAR_BIT);
    printf("    \"sizeof_char\": %zu,\n", sizeof(char));
    printf("    \"sizeof_void_p\": %zu,\n", sizeof(void*));
    printf("    \"sizeof_size_t\": %zu,\n", sizeof(size_t));
#ifdef SIZE_MAX
    printf("    \"SIZE_MAX\": \"%zu\",\n", (size_t)SIZE_MAX);
#else
    printf("    \"SIZE_MAX\": null,\n");
#endif
    printf("    \"getenv_api\": 1,\n");
    printf("    \"setenv_api\": 1,\n");
    printf("    \"unsetenv_api\": 1,\n");
    printf("    \"putenv_api\": 1,\n");
    printf("    \"strtol_api\": 1,\n");
    printf("    \"execve_api\": 1\n");
    printf("  },\n");

    /* missing_variable_marker */
    errno = 0;
    char *p_missing = getenv("HN_ENV_LAB_MISSING");
    int err_missing = errno;
    printf("  \"missing_variable\": {\n");
    printf("    \"name\": \"HN_ENV_LAB_MISSING\",\n");
    printf("    \"returned_null\": %s,\n", p_missing ? "false" : "true");
    printf("    \"errno_after\": %d\n", err_missing);
    printf("  },\n");

    /* setenv_insert_marker */
    unsetenv("HN_ENV_LAB_VALUE");
    errno = 0;
    int se_ins = setenv("HN_ENV_LAB_VALUE", "alpha", 1);
    int se_ins_err = errno;
    char *p_ins = getenv("HN_ENV_LAB_VALUE");
    char ins_copy[64] = {0};
    size_t ins_len = 0;
    if (p_ins) { ins_len = strlen(p_ins); strncpy(ins_copy, p_ins, sizeof(ins_copy)-1); }
    printf("  \"setenv_insert\": {\n");
    printf("    \"setenv_ret\": %d,\n", se_ins);
    printf("    \"errno_after\": %d,\n", se_ins_err);
    printf("    \"value\": "); json_str(ins_copy); printf(",\n");
    printf("    \"value_len\": %zu\n", ins_len);
    printf("  },\n");
    unsetenv("HN_ENV_LAB_VALUE");

    /* setenv_overwrite_false_marker */
    setenv("HN_ENV_LAB_VALUE", "alpha", 1);
    int se_of = setenv("HN_ENV_LAB_VALUE", "beta", 0);
    char *p_of = getenv("HN_ENV_LAB_VALUE");
    char of_copy[64] = {0};
    if (p_of) strncpy(of_copy, p_of, sizeof(of_copy)-1);
    printf("  \"setenv_overwrite_false\": {\n");
    printf("    \"setenv_ret\": %d,\n", se_of);
    printf("    \"result\": "); json_str(of_copy); printf("\n");
    printf("  },\n");
    unsetenv("HN_ENV_LAB_VALUE");

    /* setenv_overwrite_true_marker */
    setenv("HN_ENV_LAB_VALUE", "alpha", 1);
    char *p_before = getenv("HN_ENV_LAB_VALUE");
    char before_copy[64] = {0};
    if (p_before) strncpy(before_copy, p_before, sizeof(before_copy)-1);
    errno = 0;
    int se_ot = setenv("HN_ENV_LAB_VALUE", "beta", 1);
    int se_ot_err = errno;
    char *p_after = getenv("HN_ENV_LAB_VALUE");
    char after_copy[64] = {0};
    size_t after_len = 0;
    if (p_after) { after_len = strlen(p_after); strncpy(after_copy, p_after, sizeof(after_copy)-1); }
    printf("  \"setenv_overwrite_true\": {\n");
    printf("    \"setenv_ret\": %d,\n", se_ot);
    printf("    \"errno_after\": %d,\n", se_ot_err);
    printf("    \"before\": "); json_str(before_copy); printf(",\n");
    printf("    \"after\": "); json_str(after_copy); printf(",\n");
    printf("    \"after_len\": %zu\n", after_len);
    printf("  },\n");
    unsetenv("HN_ENV_LAB_VALUE");

    /* unsetenv_marker */
    setenv("HN_ENV_LAB_VALUE", "present", 1);
    char *p_pre_unset = getenv("HN_ENV_LAB_VALUE");
    char pre_unset_copy[64] = {0};
    if (p_pre_unset) strncpy(pre_unset_copy, p_pre_unset, sizeof(pre_unset_copy)-1);
    errno = 0;
    int unset_ret = unsetenv("HN_ENV_LAB_VALUE");
    int unset_err = errno;
    char *p_post_unset = getenv("HN_ENV_LAB_VALUE");
    printf("  \"unsetenv\": {\n");
    printf("    \"unset_ret\": %d,\n", unset_ret);
    printf("    \"errno_after\": %d,\n", unset_err);
    printf("    \"before\": "); json_str(pre_unset_copy); printf(",\n");
    printf("    \"returned_null_after\": %s\n", p_post_unset ? "false" : "true");
    printf("  },\n");

    /* empty_value_marker */
    setenv("HN_ENV_LAB_EMPTY", "", 1);
    char *p_empty = getenv("HN_ENV_LAB_EMPTY");
    size_t empty_len = p_empty ? strlen(p_empty) : 0;
    printf("  \"empty_value\": {\n");
    printf("    \"returned_null\": %s,\n", p_empty ? "false" : "true");
    printf("    \"len\": %zu,\n", empty_len);
    printf("    \"is_empty_string\": %s\n", (p_empty && empty_len==0) ? "true" : "false");
    printf("  },\n");
    unsetenv("HN_ENV_LAB_EMPTY");

    /* getenv_pointer_snapshot_marker */
    setenv("HN_ENV_LAB_VALUE", "snapshot_one", 1);
    char *p_snap1 = getenv("HN_ENV_LAB_VALUE");
    char snap1_copy[64] = {0};
    size_t snap1_len = 0;
    if (p_snap1) { snap1_len = strlen(p_snap1); strncpy(snap1_copy, p_snap1, sizeof(snap1_copy)-1); }
    setenv("HN_ENV_LAB_VALUE", "snapshot_two", 1);
    char *p_snap2 = getenv("HN_ENV_LAB_VALUE");
    char snap2_copy[64] = {0};
    size_t snap2_len = 0;
    if (p_snap2) { snap2_len = strlen(p_snap2); strncpy(snap2_copy, p_snap2, sizeof(snap2_copy)-1); }
    printf("  \"snapshot\": {\n");
    printf("    \"first_copy\": "); json_str(snap1_copy); printf(",\n");
    printf("    \"first_len\": %zu,\n", snap1_len);
    printf("    \"second_copy\": "); json_str(snap2_copy); printf(",\n");
    printf("    \"second_len\": %zu\n", snap2_len);
    printf("  },\n");
    unsetenv("HN_ENV_LAB_VALUE");

    /* putenv_alias_marker */
    static char putenv_buf[64] = "HN_ENV_LAB_ALIAS=alias_one";
    int put_ret = putenv(putenv_buf);
    char *p_alias = getenv("HN_ENV_LAB_ALIAS");
    char alias_copy[64] = {0};
    if (p_alias) strncpy(alias_copy, p_alias, sizeof(alias_copy)-1);
    printf("  \"putenv_alias\": {\n");
    printf("    \"putenv_ret\": %d,\n", put_ret);
    printf("    \"caller_buf\": \"HN_ENV_LAB_ALIAS=alias_one\",\n");
    printf("    \"getenv_value\": "); json_str(alias_copy); printf("\n");
    printf("  },\n");

    /* putenv_buffer_mutation_marker */
    memcpy(putenv_buf + 17, "alias_two", 9);
    char *p_alias2 = getenv("HN_ENV_LAB_ALIAS");
    char alias2_copy[64] = {0};
    if (p_alias2) strncpy(alias2_copy, p_alias2, sizeof(alias2_copy)-1);
    printf("  \"putenv_mutation\": {\n");
    printf("    \"caller_buf_after\": \"HN_ENV_LAB_ALIAS=alias_two\",\n");
    printf("    \"getenv_value_after\": "); json_str(alias2_copy); printf("\n");
    printf("  },\n");
    unsetenv("HN_ENV_LAB_ALIAS");

    /* invalid_name_rejection_marker */
    errno = 0;
    int se_empty = setenv("", "x", 1);
    int se_empty_err = errno;
    errno = 0;
    int se_bad = setenv("HN_ENV_LAB_INVALID=BAD", "x", 1);
    int se_bad_err = errno;
    errno = 0;
    int ue_empty = unsetenv("");
    int ue_empty_err = errno;
    errno = 0;
    int ue_bad = unsetenv("HN_ENV_LAB_INVALID=BAD");
    int ue_bad_err = errno;
    printf("  \"invalid_names\": {\n");
    printf("    \"setenv_empty_ret\": %d, \"setenv_empty_errno\": %d,\n", se_empty, se_empty_err);
    printf("    \"setenv_bad_ret\": %d, \"setenv_bad_errno\": %d,\n", se_bad, se_bad_err);
    printf("    \"unsetenv_empty_ret\": %d, \"unsetenv_empty_errno\": %d,\n", ue_empty, ue_empty_err);
    printf("    \"unsetenv_bad_ret\": %d, \"unsetenv_bad_errno\": %d\n", ue_bad, ue_bad_err);
    printf("  },\n");

    /* startup_snapshot_marker */
    const char *names[3] = {"HN_ENV_LAB_MODEL_SLOT","HN_ENV_LAB_FEATURE_LIMIT","HN_ENV_LAB_THRESHOLD_BPS"};
    char snap_vals[3][64] = {{0}};
    size_t snap_lens[3] = {0};
    int snap_present[3] = {0};
    for (int i=0;i<3;i++) {
        char *p = getenv(names[i]);
        if (p) { snap_present[i]=1; snap_lens[i]=strlen(p); strncpy(snap_vals[i], p, sizeof(snap_vals[i])-1); }
    }
    printf("  \"startup_snapshot\": {\n");
    for (int i=0;i<3;i++) {
        printf("    \"s%d_present\": %s, \"s%d_value\": ", i, snap_present[i]?"true":"false", i);
        json_str(snap_vals[i]);
        printf(", \"s%d_len\": %zu%s\n", i, snap_lens[i], i<2?",":"");
    }
    printf("  },\n");

    /* bounded_copy_marker – call getenv_bounded_copy with capacities 0,1,6,7,8 */
    setenv("HN_ENV_LAB_VALUE", "abcdef", 1);
    printf("  \"bounded_copy\": {\n");
    printf("    \"cases\": [\n");
    size_t caps[] = {0,1,6,7,8};
    for (int i=0;i<5;i++) {
        size_t cap = caps[i];
        char outbuf[32];
        memset(outbuf, 0xAA, sizeof(outbuf));
        size_t required = 0;
        int status = getenv_bounded_copy("HN_ENV_LAB_VALUE", outbuf, cap, &required);
        int sentinel_ok = 1;
        size_t bytes_written = 0;
        if (status == 0) {
            bytes_written = required;
            /* check bytes past written region still 0xAA */
            for (size_t j = required; j < sizeof(outbuf); j++) {
                if ((unsigned char)outbuf[j] != 0xAA) { sentinel_ok = 0; break; }
            }
        } else {
            /* on insufficient capacity, output buffer should be untouched */
            for (size_t j = 0; j < sizeof(outbuf); j++) {
                if ((unsigned char)outbuf[j] != 0xAA) { sentinel_ok = 0; break; }
            }
        }
        printf("      {\"capacity\": %zu, \"status\": %d, \"required\": %zu, \"bytes_written\": %zu, \"sentinel_ok\": %s}%s\n",
            cap, status, required, bytes_written, sentinel_ok ? "true" : "false", i<4?",":"");
    }
    printf("    ]\n");
    printf("  },\n");
    unsetenv("HN_ENV_LAB_VALUE");

    /* bounded_integer_config_marker – real C strtol() */
    const char *int_inputs[] = {"5","0","128","-1","5x","","999999999999999999999999999999"};
    printf("  \"bounded_int\": {\n");
    printf("    \"cases\": [\n");
    for (int i=0;i<7;i++) {
        const char *inp = int_inputs[i];
        errno = 0;
        char *endptr = NULL;
        long val = strtol(inp, &endptr, 10);
        int err = errno;
        size_t end_off = endptr ? (size_t)(endptr - inp) : 0;
        int complete = (endptr && *endptr == '\0');
        int in_range = (val >= 1 && val <= 128 && err == 0);
        int accept = complete && in_range;
        printf("      {\"input\": ");
        json_str(inp);
        printf(", \"conversion_occurred\": %s, \"parsed\": %ld, \"endptr_offset\": %zu, \"complete\": %s, \"errno\": %d, \"range_valid\": %s, \"accept\": %s}%s\n",
            (endptr != inp) ? "true" : "false",
            val, end_off, complete ? "true" : "false", err,
            in_range ? "true" : "false",
            accept ? "true" : "false",
            i<6?",":"");
    }
    printf("    ]\n");
    printf("  },\n");

    /* child_environment_vector_marker */
    const char *vec_entries[] = {
        "HN_ENV_LAB_FEATURE_LIMIT=64",
        "HN_ENV_LAB_MODEL_SLOT=blue",
        "HN_ENV_LAB_THRESHOLD_BPS=5000"
    };
    size_t vec_count = 3;
    /* build owned copies */
    char *owned[4] = {0};
    size_t total_bytes = 0;
    for (size_t i=0;i<vec_count;i++) {
        size_t len = strlen(vec_entries[i]) + 1;
        total_bytes += len;
        owned[i] = (char*)malloc(len);
        if (owned[i]) memcpy(owned[i], vec_entries[i], len);
    }
    owned[vec_count] = NULL;
    /* verify lexicographic order */
    int lex_ok = 1;
    for (size_t i=1;i<vec_count;i++) {
        if (strcmp(owned[i-1], owned[i]) > 0) { lex_ok = 0; break; }
    }
    printf("  \"child_env_vector\": {\n");
    printf("    \"count\": %zu,\n", vec_count);
    printf("    \"total_bytes\": %zu,\n", total_bytes);
    printf("    \"null_terminator\": true,\n");
    printf("    \"lexicographic\": %s,\n", lex_ok ? "true" : "false");
    printf("    \"entries\": [");
    for (size_t i=0;i<vec_count;i++) {
        json_str(owned[i] ? owned[i] : "");
        if (i+1 < vec_count) printf(", ");
    }
    printf("]\n  }\n");
    for (size_t i=0;i<vec_count;i++) free(owned[i]);

    printf("}\n");
    return 0;
}
