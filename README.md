# OCCT SDK release automation

This repository's default branch contains the automation used to detect official
Open CASCADE Technology (OCCT) releases, build lean SDK packages, qualify the
resulting artifacts, and publish immutable GitHub Releases.

The default branch intentionally does **not** vendor an OCCT source tree. Build
jobs resolve an official release from `Open-Cascade-SAS/OCCT`, peel its tag to
an exact source commit, and check out that upstream commit separately from this
repository's automation files.

## Active workflows

- `.github/workflows/build-latest-occt-sdk.yml` detects and publishes new
  stable upstream OCCT SDK releases.
- `.github/workflows/build-linux-packages.yml` builds and validates Linux SDKs.
- `.github/workflows/build-macos-packages.yml` builds and validates macOS SDKs.
- `.github/workflows/build-windows-packages.yml` builds and validates Windows SDKs.
- `.github/workflows/validate-lean-profile.yml` checks that the shared lean
  packaging profile stays consistent across platforms.

Platform-specific build and verification helpers live under
`.github/*-occt-sdk/`. Release policy, verification, and recovery material
live under `.github/occt-sdk-release/`.

## Current release

The [`occt-sdk-8.0.1`](https://github.com/precise-simulation/OCCT-sdk/releases/tag/occt-sdk-8.0.1)
release is the canonical baseline for new consumers. It was
qualified and published from automation revision
`84bfd579cf6f660a63e4cad06a6c23742df579c3` using official upstream OCCT
`V8.0.1` source commit `b8f597c677811d1f9f4d8a97f5ae2825c0353a42`.
The immutable release contains 18 assets: the qualified Windows, Linux, and
macOS SDK packages and checksums plus the exact upstream source archive and
checksum.

## Consumer quickstart

For example, download and verify the Linux x86_64 shared SDK, then extract it:

```bash
release_url=https://github.com/precise-simulation/OCCT-sdk/releases/download/occt-sdk-8.0.1
asset=opencascade-8.0.1-linux-x86_64-glibc2.17-shared-b8f597c67781.tar.gz
curl -fLO "$release_url/$asset"
curl -fLO "$release_url/$asset.sha256"
sha256sum -c "$asset.sha256"
tar -xzf "$asset"
```

Point CMake at the package configuration in the extracted SDK and require the
config package from your project:

```cmake
find_package(OpenCASCADE CONFIG REQUIRED)
target_link_libraries(my_target PRIVATE TKDESTEP TKDEIGES TKDESTL TKOffset TKMesh)
```

```bash
sdk_dir="$PWD/${asset%.tar.gz}"
cmake -S . -B build -DOpenCASCADE_DIR="$sdk_dir/lib/cmake/opencascade"
cmake --build build
```

Choose the release asset that matches the target platform, architecture, and
shared/static linkage. On macOS, the adjacent checksum can be checked with
`shasum -a 256 -c <asset>.sha256`.

The Windows static package has an additional consumer contract because OCCT
8.0.1's installed CMake package does not propagate all static-link requirements.
Static consumers must define `OCCT_STATIC_BUILD` and `OCCT_NO_PLUGINS` and link
`advapi32;gdi32;user32;wsock32;psapi;windowscodecs;winmm` in addition to
`${OpenCASCADE_LIBRARIES}`. For example:

```cmake
target_compile_definitions(my_target PRIVATE OCCT_STATIC_BUILD OCCT_NO_PLUGINS)
target_link_libraries(my_target PRIVATE ${OpenCASCADE_LIBRARIES}
  advapi32 gdi32 user32 wsock32 psapi windowscodecs winmm)
```

## Source provenance

The automation keeps the workflow revision and OCCT source revision separate:

1. the release workflow identifies an official stable upstream release;
2. the upstream tag is peeled to an exact OCCT source SHA;
3. each platform builder checks out this repository only for `.github/`
   automation and checks out `Open-Cascade-SAS/OCCT` separately at that SHA;
4. artifact manifests and release notes record the exact upstream source SHA;
5. an `occt-sdk-X.Y.Z` release tag identifies the automation revision that
   qualified and published those artifacts;
6. automatic releases also attach an exact-SHA upstream source archive and its
   SHA-256 checksum so the packaged source remains available with the immutable
   binary release.

See `.github/occt-sdk-release/README.md` for the detailed release contract and
failure/recovery rules.

## Repository history

This standalone automation repository intentionally starts with fresh Git
history and does not inherit the upstream OCCT source history. Historical fork
history and the earlier SDK releases remain available in
`precise-simulation/OCCT`; new SDK automation and releases live here.

## License

The repository retains `LICENSE_LGPL_21.txt` and
`OCCT_LGPL_EXCEPTION.txt` for OCCT licensing and provenance. SDK artifacts
built from upstream OCCT remain subject to the applicable OCCT licensing terms.
