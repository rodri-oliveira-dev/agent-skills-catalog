# MSBuild, SDK, and NuGet Review

Use this reference when a pull request changes `.csproj`, `.props`, `.targets`, `Directory.Build.*`, `Directory.Packages.props`, `global.json`, solution files, packaging, or publish settings.

## Establish the project model

Before reporting a project-system issue, determine:

- SDK-style versus legacy project format;
- target frameworks and multi-targeting;
- repository SDK pinning through `global.json`;
- Central Package Management usage;
- shared properties/targets imported from parent directories;
- library versus application packaging/deployment expectations.

MSBuild evaluation is contextual. Do not judge a project file in isolation when central props/targets can redefine behavior.

## Target frameworks and language versions

Check for:

- dropped TFMs that break supported consumers;
- new TFMs missing conditions for framework-specific dependencies/source;
- `LangVersion` increases unsupported by the selected SDK;
- target-framework upgrades that change runtime/API availability or deployment requirements;
- explicit language version settings that conflict with repository policy.

Do not require `latest`/`preview` language versions.

## Package references

Review:

- major upgrades and known breaking configuration changes;
- prerelease packages accidentally introduced into stable projects;
- duplicate versions split between project files and `Directory.Packages.props`;
- analyzer/build packages missing appropriate `PrivateAssets` when they should not flow transitively;
- a dependency changing from transitive to direct without an intentional ownership reason;
- library package dependencies that alter the consumer graph.

Do not call a package vulnerable or obsolete without evidence from the repository/tooling or an authoritative advisory.

## Conditions

Conditions are a common source of silent build differences.

Check:

- property quoting and comparison semantics;
- `$(TargetFramework)` versus `$(TargetFrameworks)` mistakes;
- configuration/platform conditions that do not match actual values;
- OS/path assumptions;
- conditions on `ItemGroup`, `PropertyGroup`, references, and target execution that unintentionally broaden/narrow scope.

## Imports and central configuration

- Check whether a local property unintentionally overrides shared `Directory.Build.props`/targets behavior.
- Avoid duplicated configuration that can drift from the repository's central source of truth.
- Check import paths for portability and existence across developer/CI environments.
- Review custom props/targets for global side effects on every project beneath a directory.

## Custom targets

For `<Target>` changes, review:

- execution ordering;
- whether it runs once or repeatedly across target frameworks;
- incremental build inputs/outputs when the target performs expensive generation;
- commands/scripts for Windows/Linux/macOS portability when CI/dev environments differ;
- correct escaping/quoting of paths and arguments;
- failures hidden with overly permissive `ContinueOnError`;
- generated outputs entering source/package/publish unexpectedly.

## Build correctness

Check changes involving:

- nullable context;
- implicit usings;
- analyzers;
- warnings-as-errors / `NoWarn` / `WarningsNotAsErrors`;
- deterministic/CI builds;
- source generators;
- generated files;
- `InternalsVisibleTo`;
- unsafe code;
- signing.

Flag broad warning suppression when it hides a real class of defects introduced by the change. Do not object to a narrow documented suppression purely on principle.

## Publish and deployment

Review changes to:

- self-contained/framework-dependent deployment;
- runtime identifiers;
- trimming;
- Native AOT;
- single-file publishing;
- ReadyToRun;
- container properties;
- content copied to output/publish;
- environment/config files included in artifacts.

Compatibility and runtime behavior matter more than whether the project uses the newest publishing feature.

## Packaging

For NuGet libraries, check:

- accidental changes to target-framework support;
- dependency exposure;
- package content paths;
- build/buildTransitive assets;
- symbols/source packaging when part of existing standards;
- package metadata required by the repository;
- public API changes that should be coordinated with package versioning.

## Common false positives

Do not claim:

- every package should be centrally managed;
- every repository needs `global.json`;
- `.slnx` is inherently better than `.sln`;
- all warnings must be errors in every environment;
- every library must multi-target;
- custom MSBuild targets are bad simply because they are complex.

Report the concrete build, compatibility, packaging, or maintenance impact.
