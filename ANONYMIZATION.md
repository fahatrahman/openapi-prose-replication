# Anonymization of this package

The files here are copies of the working artifacts, edited for anonymous review.

- Dataset-hosting account names in paths and URLs were replaced with placeholders of the same length (`anonuser01`, `anonuser02`, `anonuser_u003`), including inside nested ZIP archives. Redacted archives were rebuilt; apart from the replacements, their members are unchanged.
- Notebook platform metadata (attached dataset identifiers, execution metadata) and all cell metadata were removed. Cell source is unchanged apart from the account-name placeholders.
- Notebooks marked "cleared" in a model README have no stored outputs.
- The results spreadsheet was renamed (`stage_11_supervisor_results.xlsx` became `stage_11_results_summary.xlsx`).
- Local paths in three scripts under `Granite/verification/` were replaced with relative placeholders.

## Checksums of redacted files

Checksums recorded inside the pipeline (stage manifests, values pinned in notebooks) refer to the files before redaction. For the files below they therefore do not match the published copy, and the same applies to checksums of members inside the rebuilt archives.

| File | Replacements | SHA-256 before | SHA-256 published |
|---|---|---|---|
| `Qwen/notebooks/01_stage_01_build_canonical_corpus_and_verify_api_families.ipynb` | 21 value(s) | `764cad66789ab234d65f08df41a9ee2ec441affb354c0d6499980a9f8c2c5bfc` | `3b3f18def73d8e8201f8670a6048fcd8f43644ae2077711d6e8793142f1326dc` |
| `Qwen/notebooks/02_stage_02_slice_operations_and_measure_original_prose.ipynb` | 16 value(s) | `f969bcb5f0d05ae27d78ae4c45ac9452e5fec36a7662fd4a5f11a6a3b68d4bcf` | `525c4bb060c7188861dcac3101ddf52fecc9f002664096ff47278411871ac7ec` |
| `Qwen/notebooks/04_stage_03_build_matched_inputs_and_verify_evaluator_feasibility.ipynb` | 19 value(s) | `5b5318323f95792bbb99878625563c5f9d39e943b819ea5bfb7592a1594f5875` | `83fc10dac255072721dd4e7ca40ed2b1c7de3b4a67eff3345a13a64e354b67cb` |
| `Qwen/findings/01_stage_01_corpus_preparation/stage_01_corpus_preparation_v1.zip` | 70 value(s) | `f12282cb3824a5328661598290b70c2d5e6c8d2afcbcb13ea7e96de522417990` | `6cc467c9b4f76d2003536c9521efdf26e577b83c78c9a635247a109baab6a0ff` |
| `Qwen/findings/06_pilot_stage_05_reviewed_oracles/stage_05_fresh.zip` | 100 value(s) | `374da73563b49c8db027c108b3acb521980835c7d5ef79948ae1207bb32fc95f` | `ebec9f6069e6561e2386b030bf98e037156ce53de5e29cd42577500d438aab5e` |
| `large_files/stage_02_operation_slicing_v1.zip` | 73 value(s) | `639318eff8b69984ddf2c5c801f55dca44d817d78277023b496f7e1e27076ab2` | `4d307e2eed2a9cb57e31d6150356e6eb017de2d89c309812ea7fd8625cea82c8` |
| `Qwen/notebooks/00_stage_00_freeze_protocol_and_qualify_runtime.ipynb` | 3 value(s) | `64703caaca8eef43ea0b21d7751917745b558b6c91be20dd37835dc7b9e6126e` | `5b7c5e80a3a65f844d49e873dc80e06f85cb4c31fc5ec2ab8aa00cc121b11ee1` |
| `Qwen/notebooks/14_main_stage_07_generate_1700_outputs.ipynb` | 5 value(s) | `11c86045b58c007caddf47af79d6ec427b79650fe70072922774d4c58a5475fe` | `c9ccd9536c666ae389f3d828ed05e396954f36a4fa39b653c90e7b27eafecbef` |
| `Qwen/notebooks/15_main_stage_08_offline_evaluation_and_blinded_review.ipynb` | 6 value(s) | `feb771029dae6fcb435adebf1a3653fda20647b5f1da14aac2315d9a4889a01a` | `b2230e287f8d203bbfd45cb7ec42497c261b1105b634100de28ab31dd4b8be13` |
| `Qwen/notebooks/08_pilot_stage_07_generate_model_outputs.ipynb` | 4 value(s) | `255cdf4b087bd0a38c1e391ef0ba0f2e16289010a1b4822c9ca1763fb74b247e` | `312ea02d1527867503ccdddeabecc562ebcbf200f903f54b8cc7c46d02201549` |
| `Qwen/findings/00_stage_00_protocol_runtime/stage_00_protocol_runtime_v1.zip` | 2 value(s) | `496f3c14ca2715122d0134087714b1e3276ce125e070901595c994e3d50622a9` | `d80beaefc6cb85c6828e5cdf5d4f42c71061410fd10932870e43ac51c10d7f9c` |
| `Qwen/findings/00_stage_00_protocol_runtime/stage_00.zip` | 4 value(s) | `d90f2150ccf62488a9c3f1e467c4bd3698ca7276a155467f45169e079a846a4b` | `04e8334baefa4a56048b0439ddcd423b753e6bfc54ab3d614262292f6ca1131b` |
| `Qwen/findings/13_main_stage_06_evaluator_and_tasks/stage_06_main.zip` | 2 value(s) | `5907ac62877fcdfee6f2e590bc5351f5bbf1becc13de500b8d7b331c0fc5fed6` | `80337a0d19f6f9c790e6aad5e4f743d0e3e68ac511ab43fe02e38ef029400320` |
| `Qwen/findings/14_main_stage_07_1700_outputs/stage_07_main.zip` | 4 value(s) | `617aca020c61dc6f841e113bcdd3b6295c5846df5ad6dc6b1cb93b3562fb29a8` | `5e8559a3256699f1859a3ceb2ae0cf908a6012dad8d4f66dcda4b22d78f973ca` |
| `Qwen/findings/15_main_stage_08_evaluation_and_review/stage_08_main.zip` | 3 value(s) | `ad1bf2bd6a4fa86462fded5a37ec0ca4d72af9ae7946ce8078be46cda335ea68` | `056ebce686f7d6e2909081d72e25de1086e264dd6cf20f105a0e38ad9b5c1438` |
| `Qwen/findings/07_pilot_stage_06_evaluator_and_tasks/stage_06_fresh.zip` | 2 value(s) | `c52507e6d43d48695d5ac53d341d05a026b7e9a57f35fdd75465b903e2b87d81` | `c91a2742e7fa5c00dee544cac1f68469f8035d78f4ffe8cf6538b4c114722f97` |
| `Qwen/findings/08_pilot_stage_07_model_outputs/stage_07_fresh.zip` | 4 value(s) | `ba632b9a7ad66c94efe0255a334eb57896fed98044212ee56955902ed253ae1d` | `a5b87bdf15ec46c84205def57777f07d6be8a0676b01c266f3c9371fa86c751b` |
| `Qwen/findings/09_pilot_stage_08_corrected_review/corrected_stage_08_fresh.zip` | 3 value(s) | `03ebff585b2f10e2a916ab916961f295179dcd030824a7bf11ee71dc9eb09614` | `f54986a1e5df8baebefc993c9536f1b377b653591b4fe423f8ae4ac2032971c1` |
| `Llama/notebooks/00_protocol_runtime.ipynb` | 2 value(s) | `aed613a3a9717c094dc7dcb793545800770d775676f92bd6dbead99a5a02d828` | `52ebfe644db5b4a1d372eaa6cb15ccb76ecce60212b7ab3a180baa30976948f2` |
| `Llama/notebooks/08_main_evaluation_session1.ipynb` | 6 value(s) | `b87ac388e667fb9278b573eb1e061c022cd400739597c4464932f34495c48457` | `a56e3042e7ce0b7d71cacd9a5269bac7b3f53bfe949e00160ae0f656a61f1fd6` |
| `Llama/notebooks/08_main_evaluation_session2.ipynb` | 8 value(s) | `9bb901457246d6f7c25ed1a3ce8d1c7f4c2f4f38e2ccde43ed8a70e5cffe0ad4` | `cf241a1ca23d28de9d030b0cce338073a7b98be37e7ea960d570f96cb7469c50` |
| `Llama/notebooks/08_main_evaluation_session3.ipynb` | 8 value(s) | `8cd306e9a48f8707bf920e950c23830ba8457d9db7198fba1e90166d7c2764a7` | `54d9b08cacff779b1a14f53fa6bf22f235241db4e939719e343b53fd6a53847c` |
| `Llama/results/stage_00/stage_00_manifest.json` | 2 value(s) | `f26db8354e52c1746236fe9fee4ed978d4a6af3b1231d86d1f7126c1a2016d86` | `f7d3cfc12cbf48bddf77e95bb65669a7f6e117ec570614bda8d22780cd1dc2f8` |
| `Llama/results/stage_00/stage_00_protocol_runtime_v1.zip` | 2 value(s) | `af7d5f54e2082b8b366ea8e82ac3fb6f132f3db62470f86995d021528bf6e681` | `29de8e8296f32ed7bd017831ec7fabe869b8bd50e986b951c782c8056b2eabd6` |
| `Llama/results/stage_00_provenance/stage_00_manifest.json` | 2 value(s) | `37ad2eb3f44de30bbf9efe318abfd813576c2263c31be2f43ba110a7effcc4de` | `791def7def82b27d2e3ec7853b21b5af785f3bcb65764f141638da589e316b5f` |
| `Llama/results/stage_00_provenance/stage_00_provenance_v1.zip` | 2 value(s) | `65a905e4d69d5d1eeb546591c4082819517defe9a668a8dd8fa1410b24c849b8` | `41035a49d2efefc07ec0771d6c2109305959a50b71495264ae8c788c5092b5d8` |
| `Llama/results/stage_06/stage_06_main.zip` | 2 value(s) | `2ab850ecd73872f19d9264da6f6097673d1fb297c2535853f453c7515b14f747` | `19eebda32b7c1886d24278790a23f85c8b87166e1fc374415e74a91d91a0c073` |
| `Llama/results/stage_07/stage_07_main.zip` | 4 value(s) | `303f4fa39ba2e16dff21154dc12aa261d8067e642e1b0691bbddeed8cea0b3d7` | `14b998d0092aed93295d1aa19f8e5a3f4cfd035268d792a6e20c8857f83ac000` |
| `Llama/results/stage_08/stage_08_main.zip` | 3 value(s) | `fd17db4a2f3cc9470e0a4e4dfcc9a58f5047343644327b007b33b1a9f825f0fd` | `6dcb21eed8b6656fe1caddfb6d7c931fcd05b09047529d262a0ad2cf547a060c` |
| `Granite/notebooks/00_protocol_runtime.ipynb` | 2 value(s) | `266a830185a6425b817a2ec91d1c031f4d14b4bcd1930eeb033d387a0f672e85` | `775df1bffd86d4bdfe7e2fd57a1dd1b4bafe56fbbe807533fb7fd1eaec71e851` |
| `Granite/notebooks/08_main_evaluation_session1.ipynb` | 6 value(s) | `14c04008b76c2b89f211ad49b813bb86b878157888de3774722ba3fbe7a97f08` | `24c73dc5b20696dcd7982543d4da1098f46b41f705c964c832fe9c415de499dd` |
| `Granite/notebooks/08_main_evaluation_session2.ipynb` | 8 value(s) | `8aa8f6b1aa13050e73cf39619a0bed86dbd0af62a9c9e585da5d5b967e500a9f` | `641f3c478be3918b1f33a14d1963d534a030eb7d7e1f82db9695f95b080f9d1f` |
| `Granite/results/stage_00/stage_00_manifest.json` | 2 value(s) | `1d8e5e1df7c21b1fe06b5b1d62babbd0978ea98b5fc572bad13827256c7f311d` | `48888efb968c00f0c42875eeaece84073411da7dd59107c7237e6f8efaf8d276` |
| `Granite/results/stage_00/stage_00_protocol_runtime_v1.zip` | 2 value(s) | `3681102f604a9d5f9e67b83a4c49b7dcb3dd241a41012e54e477c692fc9cc6f6` | `5e1768819b0ab762002d5219f76e159f23bceeaa9febb2da4a33d95fac20cd79` |
| `Granite/results/stage_00_provenance/stage_00_manifest.json` | 2 value(s) | `f1eddd1cf0431ca83948d65a6656639b0355becada4e5102726941f52b3bfe8e` | `548cd271d5b13ae9815e2ee5785b2548e61c1e757afea4295b02c4ad363673eb` |
| `Granite/results/stage_00_provenance/stage_00_provenance_v1.zip` | 2 value(s) | `c7d234f849139ea03a00bf617e28fc02213a48a8d044dd2f2e880112d4d5a8aa` | `b20b5231364a3c3d025014127193bf1bcafbbbae1598f6718c9a9dd9fc830ab5` |
| `Granite/results/stage_06/stage_06_main.zip` | 2 value(s) | `2de8866a1443f9bdb1956d32eb0ba82586c57ed88189714f5de1eeb7c235cb22` | `4ca33a2d89ab976ccdfcf110fba91df204a8efe50d77f84d90176da5392ba7b5` |
| `Granite/results/stage_07/stage_07_main.zip` | 4 value(s) | `c4a86858bed98bdf45844cf8905314baa8460eca2ab89f08a2bff032bd616ee0` | `d9c0065e98e438a2081692354096be7a894146a3f56aa2b2be20bc11b89a4455` |
| `Granite/results/stage_08/stage_08_main.zip` | 3 value(s) | `cb8fa24f0bfd1a0952d4a6441c5f837d7af2bb932455895090a2868c211597a2` | `c72140579cf0a7901e4fde5aaafa29345f9417d3f886c910f76e138b6c40ae86` |

## Files added when the Qwen run and the shared pipeline were merged

The same account-name replacement (`anonuser01`, same length, applied to file contents, member names and nested archives) was applied to these archives. Redacting the originals this way reproduces the earlier redacted copies member for member for every archive that exists in both versions.

| File | SHA-256 before | SHA-256 published |
|---|---|---|
| `Qwen/findings/03_reexport_stage_00_to_02_provenance/stage_00_provenance/stage_00_provenance_v1.zip` | `a5b80c67b24a7d653e5144d87f608830b2df8b0096d55df560fac90f5b7d534f` | `afc07ccc4065ef9faa42e4365c31679808739cd2594048c101d3367a608948d0` |
| `Qwen/findings/03_reexport_stage_00_to_02_provenance/stage_01_provenance/stage_01_provenance_v1.zip` | `6dfc407af51135413bdf44beefdd09881237da53bf9f545decc7e9f209d3f7ff` | `651ca350cc1c38e5435c1aa90088f49458cfa1e65dd34a4ff13c83873023a82c` |
| `Qwen/findings/06_pilot_stage_05_reviewed_oracles/review_history/oracle_review_packets.zip` | `a6a571f810d08a7073ff52a2bb58b9b7370f631f117b95de9b0a1185b9d968b2` | `7a97ce4a15bfac097f754b8664b5fd5a6d64ff158edc2e05be50d456d4e7a220` |
| `Qwen/findings/09_pilot_stage_08_corrected_review/original_execution/original_v10_stage_08_execution_release.zip` | `210d5e7564f17602db1a720427778df942be1be4b3c3f6587aea88e87f804947` | `3ba52a4e8d980e7759f38c8d5989fe17dc403cd6ffb68bb2cb7bf0e0a93c7975` |
| `Qwen/findings/11_main_stage_10_corrected_sample_plan/stage_10_main_corrected.zip` | `a8379ab78d34b2a851baf4558ddec4638b32a1fe6930541b9e843c3d5c0f7fb1` | `76c573b21e96d44435dff6daaae937a7adc8eee7b93b8aa24ed878346edbb2a7` |
