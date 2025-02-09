#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/init.h>

static int __init paperdash_init(void) {
    pr_info("PaperDash: E-Paper SPI driver loaded\n");
    return 0;
}

static void __exit paperdash_exit(void) {
    pr_info("PaperDash: E-Paper SPI driver unloaded\n");
}

module_init(paperdash_init);
module_exit(paperdash_exit);

MODULE_LICENSE("MIT");
MODULE_AUTHOR("Edward Lin");
MODULE_DESCRIPTION("PaperDash E-Paper SPI Driver");

