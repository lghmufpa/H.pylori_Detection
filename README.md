# H. pylori Detection Database
**Reposiory of the project: Deep Learning for Helicobater Pylori Detection in Histopathological Tissue . This repository contains the dataset and the scripts used in the project**.


This repository presents the following folder structure:
- **Datasets:**
  - **Unseen**: Images that were not analysed by an pathologist, therefore, couldn't be labeled.
  - **Seen**: Images that were analysed by an pathologist, therefore, were labeled ans splited in the following directories.
    - **Non-augmented:** Images that did not go through any data augmentation process.
      -  **train**: Train set. Contains image and label files.
      -  **valid**: Validation set. Contains image and label files.
      -  **test**: Test set. Contains image and label files.
    - **Augmented:** Images that went through data augmentation process.
      -  **train_augmented**: Augmented train set. Contains image and label files.
      -  **valid_augmented**: Augmented validation set. Contains image and label files.
      -  **test**: Test set. Contains image and label files.

- **Metadata:** Contains the .csv files with metadata from the:
  - Unssen and Seen Non-augmented files (unssen_seen_metadata.csv).
  - Augemnted files (augmented_metadata.csv).
  - Label files with bounding box info (boundingbox_metadata.csv).

- **Graphics:** Contains the grpahs that describe the dataset content.

- **Scripts:** Contains the scripts used to build the dataset and it's descriptive graphics.
