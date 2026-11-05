# Upstream notices

This repository provides a local debugging project, build helpers, and adaptation patches for Apple's open-source Objective-C runtime.

The official source repositories are referenced as Git submodules under `upstream/`. Their copyright notices and licenses remain in those repositories. Generated working copies retain the upstream source headers.

Adaptations to Apple's objc4 sources remain subject to the Apple Public Source License 2.0. A copy is included in `LICENSES/APPLE_LICENSE`. Other upstream dependencies retain their own licenses; consult each submodule before redistributing their source or binaries.

The patches and compatibility helpers are intended for source-level experiments on the documented development environment. They do not represent Apple's complete shipping Objective-C runtime.
