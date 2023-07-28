# CHANGELOG



## v0.5.0 (2023-07-28)

### Chore

* chore(GH Action): not using semantic-release GH action: does not work

- raises error:
```
/usr/local/bin/python3: No module named build.__main__; &#39;build&#39; is a package and cannot be directly executed
Usage: python -m semantic_release version [OPTIONS]
Try &#39;python -m semantic_release version -h&#39; for help.

Error: Command &#39;[&#39;bash&#39;, &#39;-c&#39;, &#39;python3 -m build&#39;]&#39; returned non-zero exit status 1.
``` ([`131f75c`](https://github.com/BAMresearch/DACHS/commit/131f75ce54cb05b814a7d4c7201fe2fe85165a31))

* chore(GH Action): raising Python version for release step ([`1fe1cc6`](https://github.com/BAMresearch/DACHS/commit/1fe1cc69a812c447b071ec25a6265c11d5c9c42a))

* chore(GH Action): missing required package ([`5a48cf0`](https://github.com/BAMresearch/DACHS/commit/5a48cf0fe3c5bf6fde57171cb34f1c2400ae10f6))

* chore(GH Action): debug syntax err: test with branch specifier ([`d680829`](https://github.com/BAMresearch/DACHS/commit/d6808295b9065ebb94717d47f551b60208c5ce4c))

* chore(GH Action): debug syntax err: add another new part ([`85529c5`](https://github.com/BAMresearch/DACHS/commit/85529c50d2209ca395b6091a921de53b6a7ee4c5))

* chore(GH Action): debug syntax err: add new part ([`0572323`](https://github.com/BAMresearch/DACHS/commit/05723235fcc9b5034f76984a3700226b5b583214))

* chore(GH Action): debug syntax err: restore old version ([`7fdb2e8`](https://github.com/BAMresearch/DACHS/commit/7fdb2e8837b974185421161914051f02c70838d5))

* chore(GH Action): removed comments to check if this causes GH syntax error ([`88a2512`](https://github.com/BAMresearch/DACHS/commit/88a251299ff755a3b94d671dabca62f3dddcef27))

* chore(GH Action): updated semantic-release config for v8 ([`9c7740f`](https://github.com/BAMresearch/DACHS/commit/9c7740fd800d19938999ff97f3e2fbc5f16c45ef))

### Feature

* feat(equipment.PV): updated converters and validators

- to  work better with values from pandas.DataFrame being NaN or sth else ([`85ed382`](https://github.com/BAMresearch/DACHS/commit/85ed382c5c7559e38d918b4df5493e8201fcd12e))

* feat(Physical Values): parsing PVs from Logbook .xlsx file to PVs and storing them to HDF5

- parsing from HDF5 not tested yet
- also tests may not work yet, need to be fixed ([`9403b40`](https://github.com/BAMresearch/DACHS/commit/9403b40f6a65f1ecae426eb5002e004c78dfc17f))

### Fix

* fix(Notebook): adjusted for Dash 2.11, tests successful here ([`31ab924`](https://github.com/BAMresearch/DACHS/commit/31ab924e94f32cf1c2ef9bad6a1d87f48b457d9a))

* fix(helpers.whitespaceCleanup): handle Series object properly ([`f5e791e`](https://github.com/BAMresearch/DACHS/commit/f5e791e6a858969bf7d11b856b5abd9282b71f06))

* fix(serialization): dumpKV() omits custom dachs types now but stores type info

- adjusted GraphKV to work with the new format ([`cdbbbcc`](https://github.com/BAMresearch/DACHS/commit/cdbbbcc3a10e9bd036ca3dfdd355654f9ba6c735))

* fix(Equipment.Description): filter out NaN (set to &#39;&#39;) values while parsing ([`2da1957`](https://github.com/BAMresearch/DACHS/commit/2da1957ceb8944a2a4c1e9cd63ebc7ba8c76e733))

* fix(serialization.graphKV): fixed for node names containing colons &#39;:&#39;

- replaced by .
- colons may be preserved in the label
- colons have special meaning in graphviz
  https://graphviz.readthedocs.io/en/stable/api.html#graphviz.Digraph.edge ([`8570cbb`](https://github.com/BAMresearch/DACHS/commit/8570cbbf802ed12d5bc94fe5670eff2ab97d2d6f))

* fix(equipment.PV): reader/parser fixed for extended LogBook xslx format ([`5cfd521`](https://github.com/BAMresearch/DACHS/commit/5cfd521d5196c8d6bb008f4fe7f13859975fe9c1))

### Refactor

* refactor(serialization): removed obsolete filterStoragePaths()

- custom dachs objects are not stored anymore in dumpKV output ([`5eee1fb`](https://github.com/BAMresearch/DACHS/commit/5eee1fb899c39c3b3ab22f876022517c75eaebc8))

* refactor(serialization): debug output improved ([`850b293`](https://github.com/BAMresearch/DACHS/commit/850b2939b54bab5ba44f5113868cf9aa24ea129d))

* refactor(main): file mode change ([`795d93b`](https://github.com/BAMresearch/DACHS/commit/795d93b860ab15dcb446c1cf31085d5a336a8a38))

* refactor(General): regular python files shall not have executable bit set ([`b3635f4`](https://github.com/BAMresearch/DACHS/commit/b3635f4d983a8e10bc6b4ee18376fc33a187e19b))

* refactor(PV): class names shall be in TitleCase ([`13e9304`](https://github.com/BAMresearch/DACHS/commit/13e9304a05dcbdd802908b0090c2a25166638c28))

### Test

* test(requirements): fixed chempy version to prevent KeyError about . in formula

- see https://github.com/bjodah/chempy/issues/223 ([`6126f4e`](https://github.com/BAMresearch/DACHS/commit/6126f4eb6d9db960b9c099643ad9a74b0eadb999))

* test(PV): fixed tests for recent PV changes ([`ca51989`](https://github.com/BAMresearch/DACHS/commit/ca519892d82e65e691ab3778cf012ec4d96829e7))

### Unknown

* Updated Logbook with actual PVs and extra info ([`b0bafab`](https://github.com/BAMresearch/DACHS/commit/b0bafabdd40118de48019cdf04e4ba62e7fc09a6))


## v0.4.3-dev.7 (2023-06-14)

### Chore

* chore(GitHub Action): updated GH, tox &amp; docs config by yapy-cc

( BAMresearch/yapy-cookiecutter ) ([`87b5f67`](https://github.com/BAMresearch/DACHS/commit/87b5f67e9d23ea5b820b99171339637b361efe01))


## v0.4.3-dev.6 (2023-06-09)

### Chore

* chore(GitHub Action): define additional system packages in separate req. file ([`8d587cb`](https://github.com/BAMresearch/DACHS/commit/8d587cb22db3dcc794fe2a1088b8b4054cfb0314))

* chore(GitHub Action): debug apt package install ([`1f8a099`](https://github.com/BAMresearch/DACHS/commit/1f8a0994ee65d640b09441a3cbab3e562d625a0f))


## v0.4.3-dev.5 (2023-06-09)

### Chore

* chore(GitHub Action): debug unavailable apt package, typo fix ([`b725efb`](https://github.com/BAMresearch/DACHS/commit/b725efbb5fa1d8a58a4adf46698d623765c2d2e3))

* chore(GitHub Action): debug unavailable apt package ([`b93c54e`](https://github.com/BAMresearch/DACHS/commit/b93c54ed0b4ead2ce318a95f056c0649f620e904))

* chore(GitHub Action): debug unavailable apt package ([`7632486`](https://github.com/BAMresearch/DACHS/commit/763248640a6535672f4ebc91aea97c8ee52133e1))

* chore(GitHub Action): debug unavailable apt package ([`d74bc78`](https://github.com/BAMresearch/DACHS/commit/d74bc788373416360521308c79a66f9719d8b1bc))

* chore(GitHub Action): debug unavailable apt package ([`9af5f0c`](https://github.com/BAMresearch/DACHS/commit/9af5f0c0679157f82270dad9c6b448cd7965afca))

* chore(GitHub Action): debug unavailable apt package ([`c709f71`](https://github.com/BAMresearch/DACHS/commit/c709f717afed376c3ab18835bd4cad0fc155c21a))

* chore(GitHub Action): debug unavailable apt package ([`0d17ac9`](https://github.com/BAMresearch/DACHS/commit/0d17ac93ee71b1dcafcb6086974c0a1637d41f8b))

* chore(GitHub Action): install apt package with sudo ([`d84fdbd`](https://github.com/BAMresearch/DACHS/commit/d84fdbd06422e639a32e8e9c9caffd0b813962ae))

* chore(GitHub Action): dash shell syntax fix ([`c331db5`](https://github.com/BAMresearch/DACHS/commit/c331db550bec61b8eaebc5af7154cd87d7f662cb))

* chore(GitHub Action): Additional system package graphviz required ([`20fec31`](https://github.com/BAMresearch/DACHS/commit/20fec3149f14b88612cf50af559ad8fe283e8ece))

* chore(general): moved the notebook and convenience scripts to separate subdirs ([`60b3d87`](https://github.com/BAMresearch/DACHS/commit/60b3d87737ab09ec3dc9577b746d885ed4224349))

### Refactor

* refactor(main): separate main.py for code to be reused in tests ([`d62f195`](https://github.com/BAMresearch/DACHS/commit/d62f19530decca1cb9d0dc8b76348def58db8ad0))

* refactor(scripts): RunMultiple.sh updated for path handling ([`2eb6b01`](https://github.com/BAMresearch/DACHS/commit/2eb6b0125dbe66c3a72e99f96e11592659a28b6d))

* refactor(formatting): some fixes to agree with flake8 and isort, some reformatting by black ([`f614cb1`](https://github.com/BAMresearch/DACHS/commit/f614cb176415dcb683f2e3a366b7bfdc2ae9ff6b))

### Test

* test(structure): prevent pytest args to slip through to argparse ([`17039b3`](https://github.com/BAMresearch/DACHS/commit/17039b3ff02c1cc414558e1217ac0fe3f65a9d75))

* test(notebook): note on source .h5 files, outputs for .h5 files generated by tests earlier

- plotly cell output set to be ignored by cell meta data ([`27c3f7b`](https://github.com/BAMresearch/DACHS/commit/27c3f7b1318c410050bf315606f6806d72a02981))

* test(structure): using code from main to generate .h5 files, more dependencies ([`395b2ca`](https://github.com/BAMresearch/DACHS/commit/395b2cae8044b6091d49b7177c44d624cb3d00e3))


## v0.4.3-dev.4 (2023-06-02)

### Chore

* chore(checks): added notebook to source distrib manifest, exluded convenience scripts ([`d0fe3a2`](https://github.com/BAMresearch/DACHS/commit/d0fe3a2d49b0d9e45a9468e1c8b44b6747e0f3ae))


## v0.4.3-dev.3 (2023-06-02)

### Test

* test(Pint): fix currency units definition for latest Pint 0.22 ([`315222a`](https://github.com/BAMresearch/DACHS/commit/315222aae933d1242ca29a777536c3f57c306a17))

* test(reagent): fix PreparationDate argument ([`6bdeba5`](https://github.com/BAMresearch/DACHS/commit/6bdeba5d597926e9346226a0f13e125622e1a6be))

### Unknown

* Merge branch &#39;main&#39; of https://github.com/BAMresearch/DACHS ([`3537931`](https://github.com/BAMresearch/DACHS/commit/35379313ab1a2dfa3e450331f6778b87eab74b2b))

* Computation of solution age added to extraInfo ([`df5dd85`](https://github.com/BAMresearch/DACHS/commit/df5dd859e0194f086018a030334890ca2e4e37e5))

* added test case for AutoMOF_6 series ([`4fa9ec3`](https://github.com/BAMresearch/DACHS/commit/4fa9ec3ede82b8004abe6aac275a737895ff887d))

* preparing for AutoMOF 6&amp;7 ([`1d53806`](https://github.com/BAMresearch/DACHS/commit/1d5380676c3679e4248b678183065f217cd2188e))

* Shell script to run AutoMOF05 ([`755431d`](https://github.com/BAMresearch/DACHS/commit/755431d90364df1cbfce1784aefd468e7650b25b))

* script to pick apart the raw logs from RoWan ([`5918e0d`](https://github.com/BAMresearch/DACHS/commit/5918e0dacaaadf0ac4921f26b1a8e2a6a894730b))

* Readin example jupyter notebook launching Dash ([`afa6065`](https://github.com/BAMresearch/DACHS/commit/afa60659c206e583918d6ec1f8e1143d5734abc4))

* making a read-in structure python notebook ([`09a1e55`](https://github.com/BAMresearch/DACHS/commit/09a1e550aa0cca0acfdd0bcdacb02f9af10ae908))


## v0.4.3-dev.2 (2023-05-04)

### Style

* style(readers): trailing whitespace (W291) removed ([`441a4c4`](https://github.com/BAMresearch/DACHS/commit/441a4c4fb65b9844d9436b095c642046c4a35409))


## v0.4.3-dev.1 (2023-05-04)

### Style

* style(structure): black formatter ([`81f160f`](https://github.com/BAMresearch/DACHS/commit/81f160f875bdf0295a23aa2c7c99fd6f98552bbf))

### Unknown

* tests(structure): set AMSET in tests to succeed ([`e7740a5`](https://github.com/BAMresearch/DACHS/commit/e7740a5dbf703ba20c1b931de9e41a4398be79cf))

* removing superfluous weight determination ([`5ff5fd9`](https://github.com/BAMresearch/DACHS/commit/5ff5fd99e5792818bf39c7136ea6bad0397b6f95))

* reimplementing calibration and CLI AMSET option ([`9a4c70f`](https://github.com/BAMresearch/DACHS/commit/9a4c70f8bbfb5fe53331188518e324068f91b6ff))


## v0.4.2 (2023-04-20)

### Documentation

* docs(general): logo ([`febf8f0`](https://github.com/BAMresearch/DACHS/commit/febf8f04f9d5bf59652e3dcba269659e85d6f40a))

### Fix

* fix(serialization): Graph SVG with transparent background ([`366287c`](https://github.com/BAMresearch/DACHS/commit/366287c12109ded89c39dc91519c9e955ed27806))


## v0.4.1 (2023-04-18)

### Fix

* fix(GitHub Actions): Make new release only if tests succeed ([`94f7a25`](https://github.com/BAMresearch/DACHS/commit/94f7a25b9bb0021b27b267d7e717921d015a185a))

* fix(requirements): graphviz added for tests ([`a06f87d`](https://github.com/BAMresearch/DACHS/commit/a06f87de270810c613f822c3168b409fba201e78))


## v0.4.0 (2023-04-17)

### Documentation

* docs(visualization): Generate SVG Graph in __main__

- refactored serialization.dumpKV
- added serialization.filterStoragePaths
- first one generates a key/value dump with all custom objects (needed for type info later)
  - second function filters custom objects out which are incompat. with mcsas.McHDF routines
  - former key/value dump is used for graph generation ([`31f38f9`](https://github.com/BAMresearch/DACHS/commit/31f38f9fbea9fd16d87a65f7c908253a970d5f8c))

* docs(visualization): Graph building code added, WIP

- and for reference later, will next be cleaned up considerably ([`1e1ffed`](https://github.com/BAMresearch/DACHS/commit/1e1ffed5c129ba8d6299fbf2bf0148b2ab4afd08))

### Feature

* feat(serialization): use the ID for path prefix at singular objects as well

- instead of the provided prefix (hope no side effects included) ([`60a08eb`](https://github.com/BAMresearch/DACHS/commit/60a08eb256f6a920d0e7e047025fa28418029e29))

### Fix

* fix(data import): whitespace cleanup for texts/descriptions

- added a helper function to be used in multiple places
- discussion needed if this is a wanted feature ([`005be00`](https://github.com/BAMresearch/DACHS/commit/005be006aed3f8055db566804e0ac71e0a9f7226))

* fix(ExperimentalSetupClass): removing redundant whitespace from description ([`5429102`](https://github.com/BAMresearch/DACHS/commit/542910217cd0c5bf1b1e96ac919a00739aa6ccce))

* fix(readers): unwanted DataFrame string formatting ([`880ca0d`](https://github.com/BAMresearch/DACHS/commit/880ca0d1195f90cd244ef05189019149a314785b))

### Refactor

* refactor(ExperimentalSetupClass): comment about intended behaviour ([`9a41f7b`](https://github.com/BAMresearch/DACHS/commit/9a41f7be0e57cf94f506e354c91f95acc2392ff7))


## v0.3.0 (2023-04-05)

### Documentation

* docs(structure): fix format ([`4ccaf91`](https://github.com/BAMresearch/DACHS/commit/4ccaf91e6bd81e263ca4b438e4a76d2573868046))

* docs(readme): notes on command line usage ([`4d11686`](https://github.com/BAMresearch/DACHS/commit/4d11686b0921027590e370c64ffad94c9699599a))

### Feature

* feat(command line): new parameter -o allows to specify location and name of HDF5 output file ([`fab741a`](https://github.com/BAMresearch/DACHS/commit/fab741a09d924e59d24f53d5375c62b9dc758e2d))

### Fix

* fix(command line): typo in usage texts ([`cf39d14`](https://github.com/BAMresearch/DACHS/commit/cf39d142785de9b0c767dfa5d83f1eed019c61cd))

### Refactor

* refactor(serialization): use McHDF.storeKVPairs avoids separate loop ([`34b9cd9`](https://github.com/BAMresearch/DACHS/commit/34b9cd93aaf6a490ec24c2b2f88d510994c9b988))

* refactor(serialization): add type info ([`1e946d4`](https://github.com/BAMresearch/DACHS/commit/1e946d4ef2eb49c26fe465dd8d2a09bfbb6ae613))

* refactor(serialization): rename storagePaths() -&gt; dumpKV() ([`4ac7f96`](https://github.com/BAMresearch/DACHS/commit/4ac7f960cc7a9a1ffaa81d12fc2f4e505e0b2d79))

* refactor(structure): main module reuses structure.create() ([`be72352`](https://github.com/BAMresearch/DACHS/commit/be723521685146a827e1d3b6dc59b83b07fd966c))

* refactor(structure): moved testing code to separate module for reuse ([`6b78abf`](https://github.com/BAMresearch/DACHS/commit/6b78abf927af108a02f6b080b6730575aaffcfdd))

* refactor(root): rename top-level class to more meaningful name *Experiment* ([`0fe03dc`](https://github.com/BAMresearch/DACHS/commit/0fe03dcc86a4ce08e7d1e8608792bb76fd27a426))


## v0.2.0 (2023-04-04)

### Documentation

* docs(readme): info &amp; reminder how to get stdout/stderr with pytest ([`20fc960`](https://github.com/BAMresearch/DACHS/commit/20fc9601a9675882fdc4119349291f2c2a6a1fb6))

### Feature

* feat(ComponentMasses): store as dict associated to their respective Component

- previously, ComponentMasses were stored indexed while the componentlists with their component IDs ([`a797b0b`](https://github.com/BAMresearch/DACHS/commit/a797b0b61bbd754eed46d80b1aafdc63d5898b0f))

* feat(serialization): use object IDs instead of numerical index where available ([`fef04b0`](https://github.com/BAMresearch/DACHS/commit/fef04b051529510867843ab1721398acced6d3ce))

### Style

* style(serialization): fix file header

- previous one indicates an executable python file, resulting in automatic file mode change (exec) by the editor ([`029c20c`](https://github.com/BAMresearch/DACHS/commit/029c20c94823a30c92b20b468b1db5fd78cb8ebd))

### Unknown

* tests(structure): commented core for dumping all storage paths

for debugging ([`450d660`](https://github.com/BAMresearch/DACHS/commit/450d66084076d13b27028fbf5e328f86ce89be1a))


## v0.1.2 (2023-04-03)

### Fix

* fix(Serialization): store lists of quantities, fixes #7 ([`d311d5b`](https://github.com/BAMresearch/DACHS/commit/d311d5bd075cb5c9c465819301b5fb8d38652eaf))

* fix(EquipmentList): price unit parsing ([`971a54d`](https://github.com/BAMresearch/DACHS/commit/971a54d6b98e47e27b55520604f356f83d05f525))

### Refactor

* refactor(Tests): mcsas3 can be installed with pip now

- remove relative local imports of mcsas3 ([`4d17768`](https://github.com/BAMresearch/DACHS/commit/4d177680192e04ca0a9dcfba8ed339f22dc9008f))


## v0.1.2-dev.3 (2023-03-31)

### Style

* style(documentation): comment formatting ([`1129c56`](https://github.com/BAMresearch/DACHS/commit/1129c56faf7ce26fabdc43f3f113a269ca54e8b8))


## v0.1.2-dev.2 (2023-03-31)

### Documentation

* docs(General): inheritance diagram in reference ([`946cdd8`](https://github.com/BAMresearch/DACHS/commit/946cdd838430b619c4fe9bee53039774b17ef98e))

### Style

* style(changelog): version number prefixed by v ([`1840736`](https://github.com/BAMresearch/DACHS/commit/18407365ab6927c52d4fdecdf256ffc0f6c46c51))


## v0.1.2-dev.1 (2023-03-28)

### Chore

* chore(GitHub Action): handle empty pages branch ([`3d3a3d7`](https://github.com/BAMresearch/DACHS/commit/3d3a3d72b2877f948179c055bce701b2078137ba))


## v0.1.1 (2023-03-28)

### Chore

* chore(general): let git ignore hdf5 generated by tests ([`9f83d1a`](https://github.com/BAMresearch/DACHS/commit/9f83d1afa5003e297bffcf4f6efa19bb5e73904a))

* chore(GitHub Action): workflow definitions and templates ([`ab175ac`](https://github.com/BAMresearch/DACHS/commit/ab175ac6e9227935360174c041558d648b71bfab))

* chore(general): pre-commit hook should exclude diagrams ([`774be5c`](https://github.com/BAMresearch/DACHS/commit/774be5c4b706c5bf209a7885470595ed98e1536b))

* chore(general): pre-commit hook config added ([`984a284`](https://github.com/BAMresearch/DACHS/commit/984a284900f15287700de8f0383e32cc78ae6a72))

* chore(project): removed incomplete and obsolete requirements on top level ([`55898d3`](https://github.com/BAMresearch/DACHS/commit/55898d34e4e64c59e7991c21cb83afb5febb6be6))

* chore(project): pyproject.toml replaces setup.* and versioneer

- moved dachs source code to *src* subdir ([`7e34461`](https://github.com/BAMresearch/DACHS/commit/7e344619aee8cb87d25996d22dccf0ca0e6489cf))

* chore(project): cookiecutter config ([`b79ab8d`](https://github.com/BAMresearch/DACHS/commit/b79ab8d9aeee68a02f1a918450e7c0c857e04f39))

* chore(project): gitignore updated ([`c0eae7a`](https://github.com/BAMresearch/DACHS/commit/c0eae7a7971e783ec3ff8f4290fb4155fd5833ec))

* chore(project): general notes on contributing ([`b461862`](https://github.com/BAMresearch/DACHS/commit/b46186224b5309fea87897110c5c70de68cd6890))

* chore(project): editor config ([`1c603a9`](https://github.com/BAMresearch/DACHS/commit/1c603a932d3166e6c7c36dd81833893aa07499b3))

### Documentation

* docs(general): disable link check temporarily ([`332a112`](https://github.com/BAMresearch/DACHS/commit/332a112064f4727461a7e2dd3b4de4cd829bf0d3))

* docs(general): remove section title ([`d1fd17b`](https://github.com/BAMresearch/DACHS/commit/d1fd17b119e2765e014e6f929b0cfccd1061a1b3))

* docs(general): initial setup ([`a490cb1`](https://github.com/BAMresearch/DACHS/commit/a490cb1fb7210160eb52ae428de22b340ffb389d))

* docs(project): readme updated ([`caed30c`](https://github.com/BAMresearch/DACHS/commit/caed30c33f9528cc7471fabca92d0e01549ea4a3))

### Fix

* fix(reagent): adjust units and method names for tests to succeed ([`0b5b21e`](https://github.com/BAMresearch/DACHS/commit/0b5b21eb4985955f03629e385b979244e4f0a3e0))

### Refactor

* refactor(general): fix ureg imports ([`38e7a19`](https://github.com/BAMresearch/DACHS/commit/38e7a1926bd94bf37d31ff26ec5528ed0dc339ef))

### Style

* style(general): satisfy flake8 ([`ce44d64`](https://github.com/BAMresearch/DACHS/commit/ce44d649c5c3653a08d646b749b7f2c4bb3af68c))

* style(general): code formatting line length set to 115 ([`d013773`](https://github.com/BAMresearch/DACHS/commit/d01377318944d72a0a5911e933be4f42eb80a725))

* style(general): reformat main.py, whitespace fixes ([`7b9954b`](https://github.com/BAMresearch/DACHS/commit/7b9954b47594a953459e23042b518386916020f1))

* style(general): isort imports ([`0467ca3`](https://github.com/BAMresearch/DACHS/commit/0467ca37972cf42e328e280ce4b97338e3e99e15))

* style(general): formatted with black ([`1b67618`](https://github.com/BAMresearch/DACHS/commit/1b6761825cb0b2b8d0b800c25e8ce36d9b772611))

* style(line length): 115) ([`4b19763`](https://github.com/BAMresearch/DACHS/commit/4b19763770de89ea4edc10d4cfd923399b02823a))

### Unknown

* v0.1.0 ([`e9e288f`](https://github.com/BAMresearch/DACHS/commit/e9e288f0ffe678e5a65ad825167888f8c1b7c845))

* Many small fixes, now also runs from CLI ([`a06bb98`](https://github.com/BAMresearch/DACHS/commit/a06bb98aadccb77f5146684e5c40b761398e0cd7))

* adding yield, ML ratio, more test cases ([`3fe80a9`](https://github.com/BAMresearch/DACHS/commit/3fe80a9b5ebfd0a842c9fe6772734ede885a578f))

* Fix for the DACHS paths issue and other minor ([`6dc1362`](https://github.com/BAMresearch/DACHS/commit/6dc1362117f9b8f1fa33b6faaf973e062842c539))

* added the reaction mixture and automatic mm calcs. ([`36a90df`](https://github.com/BAMresearch/DACHS/commit/36a90df5d1b97b0735d133698ef7da42632561b4))

* tests passing ([`9aa39ef`](https://github.com/BAMresearch/DACHS/commit/9aa39ef97ab85710f1709c5930b51d72aa83e882))

* Mixture class operational, structure test broken. ([`e5d8e7e`](https://github.com/BAMresearch/DACHS/commit/e5d8e7e953442abe59cf736ebf093fbca9890861))

* Updated naming and start on Mixture class. ([`6846636`](https://github.com/BAMresearch/DACHS/commit/68466365c508b92a91e96b96673859e145be3b16))

* adjusting reagent, but will rewrite mixture ([`44f9108`](https://github.com/BAMresearch/DACHS/commit/44f910817aeda882046b18dcefaf5161f5867081))

* Provisioning some essential derived data on mixes ([`f657f79`](https://github.com/BAMresearch/DACHS/commit/f657f79cb9e9ad25d54e05f36ad50235f83543a7))

* added price per volume and mass to reagent ([`a084f21`](https://github.com/BAMresearch/DACHS/commit/a084f21a8305cc81f88a7b97bfc8cfff22ee8e67))

* bugfixes ([`976b687`](https://github.com/BAMresearch/DACHS/commit/976b687297f60d8c009a570492b5a118e7c09301))

* equipment and experimentalSetup unit test ([`2750dcd`](https://github.com/BAMresearch/DACHS/commit/2750dcdec472c432c2ff2abea42314d130fee062))

* Merge branch &#39;main&#39; of BAMresearch/DACHS ([`ced27a3`](https://github.com/BAMresearch/DACHS/commit/ced27a3ae63a09603c74a8238856e061b332b91a))

* Changed UID to ID and fixed excel read ([`a1ccde0`](https://github.com/BAMresearch/DACHS/commit/a1ccde0d1d325fa5d441e7e09579df99d53953d5))

* using updated McHDF.storeKV() ([`e7fa4de`](https://github.com/BAMresearch/DACHS/commit/e7fa4ded170c1d42a796397d4ac3c3df283a6a2a))

* disabled debug output ([`4621d21`](https://github.com/BAMresearch/DACHS/commit/4621d21a8296c1fbe15fc4178174d2d2905daaf7))

* using PurePath for hdf5 path, to work in Windows as well ([`3c2f4d3`](https://github.com/BAMresearch/DACHS/commit/3c2f4d34ed784522e9743de1f6484d80b424ee25))

* using PurePosixPath for hdf5 path not being filesystem related ([`d9caa87`](https://github.com/BAMresearch/DACHS/commit/d9caa8701cc5cac2d86ceca092b34bf2a7839821))

* Merge branch &#39;main&#39; of https://github.com/BAMresearch/DACHS ([`6ddeac7`](https://github.com/BAMresearch/DACHS/commit/6ddeac75acb629316e8932a5be1d7ad849f914ed))

* remove defaults for required fields ([`90487d5`](https://github.com/BAMresearch/DACHS/commit/90487d5ef995a3ab489a1d975bbc7265caec0c8d))

* hdf5 export in test_integral() using McSAS3 writer ([`4b627d8`](https://github.com/BAMresearch/DACHS/commit/4b627d8ba920c66c9864514f79571c8711d9eea6))

* fixed test_integral() ([`22257c7`](https://github.com/BAMresearch/DACHS/commit/22257c72d93df9c0299e6959dd69a3e6efbd6972))

* removed empty file ([`eb4ad06`](https://github.com/BAMresearch/DACHS/commit/eb4ad069ed15cab926dc38bbbfd876baf612391c))

* Adding derived parameters extractors, not yet work ([`90dcf7f`](https://github.com/BAMresearch/DACHS/commit/90dcf7f451b42fdde17a47212f6cc02c1e626a1e))

* Modified support for derived parameters ([`404a746`](https://github.com/BAMresearch/DACHS/commit/404a746801afebc270034ec73eaaa89f0d567dda))

* Added readers for message log and starting compoun ([`b04479f`](https://github.com/BAMresearch/DACHS/commit/b04479f972aa98c06b51116f118267cb951d7ff1))

* Added RawLogMessage tests ([`0343aeb`](https://github.com/BAMresearch/DACHS/commit/0343aeb0ef2581bc80be23db4293b9b970a83950))

* Created and moved pytests to tests directory ([`24541c2`](https://github.com/BAMresearch/DACHS/commit/24541c25938e69a599c173d9df25ced7411a2158))

* file name typo ([`e1c09cf`](https://github.com/BAMresearch/DACHS/commit/e1c09cf74ba28109284e00c4d7d5832ba8c0d82f))

* let git ignore macOS file meta data ([`cfc8642`](https://github.com/BAMresearch/DACHS/commit/cfc86423166f1745c347fd0e076e5105721574bd))

* Change datacass factory for optionals. test update ([`05ab72d`](https://github.com/BAMresearch/DACHS/commit/05ab72d2c54fcbb77211cf390d51e5b86af84c5c))

* small modifications to get the test working ([`70ba6d1`](https://github.com/BAMresearch/DACHS/commit/70ba6d1ffb9fa497dcb010a4371267e0cb2b55b5))

* packaging and versioneer. ([`7acd484`](https://github.com/BAMresearch/DACHS/commit/7acd4846d6520e14d5653a4d4b904e5dca356444))

* support for concentration calculations in mixture ([`c4ff11b`](https://github.com/BAMresearch/DACHS/commit/c4ff11b42859fd874ab886e9445daaaa5b66311e))

* Updates. Can now do mixtures of reagents ([`0ed07a6`](https://github.com/BAMresearch/DACHS/commit/0ed07a6db4b43a10bb9fbaafd2a3dc3853d3a6e0))

* probably better with raw strings. ([`327ba00`](https://github.com/BAMresearch/DACHS/commit/327ba00289dcc874105fb802a84cc72a08522200))

* addition of a UID, for storing in HDF5 tree ([`8783109`](https://github.com/BAMresearch/DACHS/commit/8783109e3921e27d7f02b41fac820db5c75a3afc))

* unit and unit conversions added. ([`0557be3`](https://github.com/BAMresearch/DACHS/commit/0557be33e817e7a183b1894b4de73c4d2969f19e))

* Added units support, see MolarMass ([`16ee937`](https://github.com/BAMresearch/DACHS/commit/16ee9371644f6ea4ab8e33aa323588ace87ee440))

* reagent now has a convenient items() iterable ([`8c1914b`](https://github.com/BAMresearch/DACHS/commit/8c1914b65339a1793a99a06975dd97388ca11f6e))

* Reagent class, just as example ([`331be46`](https://github.com/BAMresearch/DACHS/commit/331be460b0305de7028af7b4fa1306a53303dcd1))

* Initial commit ([`b0a911d`](https://github.com/BAMresearch/DACHS/commit/b0a911d43c697a2d9d6b9cdbde97ea0e76d57604))
