// Local macOS 27 ABI bridges for experimenting with Apple's public objc4-951.7.
// New system frameworks import these names; upstream uses the older internal names.
extern "C" __attribute__((visibility("default")))
IMP objc_lookUpImpOrForward(id object, SEL selector, Class cls, int behavior) {
    return lookUpImpOrForward(object, selector, cls, behavior);
}

extern "C" __attribute__((visibility("default")))
const struct mach_header **objc_copyImageHeaders(unsigned int *outCount) {
    mutex_locker_t lock(runtimeLock);
    unsigned int count = 0;
    for (auto *hi = FirstHeader; hi; hi = hi->getNext()) ++count;
    auto **result = (const struct mach_header **)calloc(count + 1, sizeof(struct mach_header *));
    if (!result) { if (outCount) *outCount = 0; return nullptr; }
    unsigned int index = 0;
    for (auto *hi = FirstHeader; hi; hi = hi->getNext())
        result[index++] = (const struct mach_header *)hi->mhdr();
    if (outCount) *outCount = count;
    return result;
}
