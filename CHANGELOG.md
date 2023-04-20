
Changelog
=========

% <!--next-version-placeholder-->

## v0.4.2 (2023-04-20)
### Fix
* **serialization:** Graph SVG with transparent background ([`366287c`](https://github.com/BAMresearch/DACHS/commit/366287c12109ded89c39dc91519c9e955ed27806))

### Documentation
* **general:** Logo ([`febf8f0`](https://github.com/BAMresearch/DACHS/commit/febf8f04f9d5bf59652e3dcba269659e85d6f40a))

## v0.4.1 (2023-04-18)
### Fix
* **GitHub Actions:** Make new release only if tests succeed ([`94f7a25`](https://github.com/BAMresearch/DACHS/commit/94f7a25b9bb0021b27b267d7e717921d015a185a))
* **requirements:** Graphviz added for tests ([`a06f87d`](https://github.com/BAMresearch/DACHS/commit/a06f87de270810c613f822c3168b409fba201e78))

## v0.4.0 (2023-04-17)
### Feature
* **serialization:** Use the ID for path prefix at singular objects as well ([`60a08eb`](https://github.com/BAMresearch/DACHS/commit/60a08eb256f6a920d0e7e047025fa28418029e29))

### Fix
* **data import:** Whitespace cleanup for texts/descriptions ([`005be00`](https://github.com/BAMresearch/DACHS/commit/005be006aed3f8055db566804e0ac71e0a9f7226))
* **ExperimentalSetupClass:** Removing redundant whitespace from description ([`5429102`](https://github.com/BAMresearch/DACHS/commit/542910217cd0c5bf1b1e96ac919a00739aa6ccce))
* **readers:** Unwanted DataFrame string formatting ([`880ca0d`](https://github.com/BAMresearch/DACHS/commit/880ca0d1195f90cd244ef05189019149a314785b))

### Documentation
* **visualization:** Generate SVG Graph in __main__ ([`31f38f9`](https://github.com/BAMresearch/DACHS/commit/31f38f9fbea9fd16d87a65f7c908253a970d5f8c))
* **visualization:** Graph building code added, WIP ([`1e1ffed`](https://github.com/BAMresearch/DACHS/commit/1e1ffed5c129ba8d6299fbf2bf0148b2ab4afd08))

## v0.3.0 (2023-04-05)
### Feature
* **command line:** New parameter -o allows to specify location and name of HDF5 output file ([`fab741a`](https://github.com/BAMresearch/DACHS/commit/fab741a09d924e59d24f53d5375c62b9dc758e2d))

### Fix
* **command line:** Typo in usage texts ([`cf39d14`](https://github.com/BAMresearch/DACHS/commit/cf39d142785de9b0c767dfa5d83f1eed019c61cd))

### Documentation
* **structure:** Fix format ([`4ccaf91`](https://github.com/BAMresearch/DACHS/commit/4ccaf91e6bd81e263ca4b438e4a76d2573868046))
* **readme:** Notes on command line usage ([`4d11686`](https://github.com/BAMresearch/DACHS/commit/4d11686b0921027590e370c64ffad94c9699599a))

## v0.2.0 (2023-04-04)
### Feature
* **ComponentMasses:** Store as dict associated to their respective Component ([`a797b0b`](https://github.com/BAMresearch/DACHS/commit/a797b0b61bbd754eed46d80b1aafdc63d5898b0f))
* **serialization:** Use object IDs instead of numerical index where available ([`fef04b0`](https://github.com/BAMresearch/DACHS/commit/fef04b051529510867843ab1721398acced6d3ce))

### Documentation
* **readme:** Info & reminder how to get stdout/stderr with pytest ([`20fc960`](https://github.com/BAMresearch/DACHS/commit/20fc9601a9675882fdc4119349291f2c2a6a1fb6))

## v0.1.2 (2023-04-03)
### Fix
* **Serialization:** Store lists of quantities, fixes #7 ([`d311d5b`](https://github.com/BAMresearch/DACHS/commit/d311d5bd075cb5c9c465819301b5fb8d38652eaf))
* **EquipmentList:** Price unit parsing ([`971a54d`](https://github.com/BAMresearch/DACHS/commit/971a54d6b98e47e27b55520604f356f83d05f525))

### Documentation
* **General:** Inheritance diagram in reference ([`946cdd8`](https://github.com/BAMresearch/DACHS/commit/946cdd838430b619c4fe9bee53039774b17ef98e))

## v0.1.1 (2023-03-28)
### Fix
* **reagent:** Adjust units and method names for tests to succeed ([`0b5b21e`](https://github.com/BAMresearch/DACHS/commit/0b5b21eb4985955f03629e385b979244e4f0a3e0))

### Documentation
* **general:** Disable link check temporarily ([`332a112`](https://github.com/BAMresearch/DACHS/commit/332a112064f4727461a7e2dd3b4de4cd829bf0d3))
* **general:** Remove section title ([`d1fd17b`](https://github.com/BAMresearch/DACHS/commit/d1fd17b119e2765e014e6f929b0cfccd1061a1b3))
* **general:** Initial setup ([`a490cb1`](https://github.com/BAMresearch/DACHS/commit/a490cb1fb7210160eb52ae428de22b340ffb389d))
* **project:** Readme updated ([`caed30c`](https://github.com/BAMresearch/DACHS/commit/caed30c33f9528cc7471fabca92d0e01549ea4a3))


## v0.1.0 (2023-03-17)

* First release
* Some classes describing the experimental setup and involved materials
* Test data
* Test routines parsing the test data, building the object representation
