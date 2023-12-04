**Note**: This repository is modifed based on the [original codebase](https://github.com/jietan/openreview-to-pmlr) from Jie Tan. The scripts are updated to support the latest OpenReview APIs. For CoRL 2023, we asked the authors to include the appendices at the end of the camera-ready papers and did not allow other supplementary files. Instead, we provided an option for authors to add a URL link to project websites and additional resources.

# openreview-to-pmlr
This is a reference for conference publication chairs to publish proceedings at PMLR (https://proceedings.mlr.press/). It implements an automatic generation pipeline, including downloading papers and supplementary materials from OpenReview, removing video files from supplementary materials, and generating the bibtex file for PMLR publication. You can find the bibtex specification here: https://proceedings.mlr.press/spec.html.

The code uses CoRL 2023 (https://corl2023.org/) as an example. Feel free to modify it to suit your need. No technical support will be provided for this repository.

## To download papers from OpenReview:
```
python download_corl_2023.py -o <path_to_download> --get_pdfs --get_supplementary
```
You need to change CONFERENCE_NAME and CONFERENCE_INVITATION in the code for your own conference.

## To remove mp4 files from the supplementary zip files:
```
python del_mp4_from_supp_zip.py -i <path_with_zip_files> -o <output_path>
```
Note that the input zip files will not be altered. All the modified zip files are written to the output_path.

## To generate the bibtex file for PMLR:
```
python create_pmlr_bib.py -i <input_path> -o <output_path>
```
The input_path should point to path_to_download when you ran download_corl_2023.py. The output_path will contain the corl23.bib and all the files that are renamed based on PMLR's requirement.

You need to change CONFERENCE_NAME and ORAL_PAPER_IDS in the code for your own conference. In this file, I assumed that there were two sections: orals and posters. If your conference has only one section or more than two sections, please search for "is_poster" in the code and modify accordingly.

