// Local runtime playground. Edit this file to add experiments.
#import <Foundation/Foundation.h>
#import <objc/runtime.h>
#import <dlfcn.h>
#import <stdio.h>
#import <string.h>

@interface RuntimeProbe : NSObject
@property(nonatomic) NSInteger age;
- (NSInteger)answer;
@end
@implementation RuntimeProbe
+ (void)load { puts("RuntimeProbe +load"); }
+ (void)initialize {
    if (self == [RuntimeProbe class]) puts("RuntimeProbe +initialize");
}
- (NSInteger)answer { return self.age + 1; }
@end

int main(void) {
    Dl_info info = {};
    dladdr((const void *)&objc_getClass, &info);
    printf("objc_getClass loaded from: %s\n", info.dli_fname ?: "unknown");
    if (!info.dli_fname || !strstr(info.dli_fname, "/.build/staging/usr/lib/libobjc.A.dylib")) {
        fputs("ERROR: local runtime not loaded. Use the objcDebug scheme or support/run.sh.\n", stderr);
        return 2;
    }
    @autoreleasepool {
        __weak RuntimeProbe *weakProbe;
        @autoreleasepool {
            RuntimeProbe *probe = [RuntimeProbe new];
            probe.age = 41;
            weakProbe = probe;
            static char associationKey;
            objc_setAssociatedObject(probe, &associationKey, @"local-runtime", OBJC_ASSOCIATION_COPY_NONATOMIC);
            NSInteger value = [probe answer];
            printf("message result: %ld, association: %s\n", (long)value,
                   [objc_getAssociatedObject(probe, &associationKey) UTF8String]);
            if (value != 42 || weakProbe != probe) return 3;
        }
        if (weakProbe != nil) return 4;
        puts("PASS: allocation, message dispatch, association, ARC, weak clearing, autorelease pools");
    }
    return 0;
}
