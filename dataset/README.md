
# Identification of Aldosterone Nodules in Surrenal Tissue WSIs

**goal**: detect and segment aldosterone-producing nodules within Whole Slide Images (WSIs) of surrenal tissue using multiple staining modalities.

## 📊 Dataset Overview & Statistics

The initial dataset exploration revealed a highly specific and clinical-grade cohort structure:

* **Total Patients:** 2 unique individuals (Patient IDs: `261785` and `265301`).
* **Total Digital Slides:** 26 Whole Slide Images (WSIs) in `.ndpi` format.
* **Staining Modalities:**
* **H&E (Hematoxylin and Eosin):** Standard histological stain for morphological context (13 slides total).
* **CYP11B2 (Immunohistochemistry):** Specific antibody staining used to pinpoint and highlight aldosterone-producing functional nodules (13 slides total).



### Distribution per Patient

The dataset is split across the two cohorts as follows:

* **Patient 261785:** 20 WSIs (10 H&E pairs and 10 CYP11B2 pairs).
* **Patient 265301:** 6 WSIs (3 H&E pairs and 3 CYP11B2 pairs).

### Ground Truth (GT) Status

There are **26 ground truth files** located in the `ground_truth/CY` directory, corresponding exactly to the functional regions:

* **Binary Masks (`_mask.png`):** 13 files representing the precise pixel-level nodule boundaries.
* **Overlays (`_overlay.png`):** 13 files providing human-readable visual reference mappings over the original tissue.
* **Alignment Key:** Training slides and Ground Truth masks must be aligned and paired using a composite unique key: `(patient_id, metadata)` (e.g., pairing slide `1B` of patient `261785` with its matching mask).

*Note*: *Ground truth are relative to CYP11B2 WSI, we need to generate the H&E ones* 

---

## 🔍 WSI Pyramidal Structure

The `.ndpi` whole slide images are stored using a multi-resolution pyramidal framework containing **9 distinct zoom levels**. A typical H&E slide in this dataset follows this resolution scaling:

| Pyramidal Level | Dimensions (Width × Height) | Downsample Factor | Best Use Case |
| --- | --- | --- | --- |
| **Level 0** | **(145920, 92928)** | **1.0x (Max)** | High-res cellular patch extraction for model training. |
| Level 1 | (72960, 46464) | 2.0x | Macro-cellular structures analysis. |
| Level 2 | (36480, 23232) | 4.0x | Glandular layer recognition. |
| Level 3 | (18240, 11616) | 8.0x | Tissue morphology mapping. |
| Level 4 | (9120, 5808) | 16.0x | General region-of-interest screening. |
| Level 5 | (4560, 2904) | 32.0x | Rapid structure evaluation. |
| Level 6 | (2280, 1452) | 64.0x | Low-res spatial layout mapping. |
| Level 7 | (1140, 726) | 128.0x | Micro-thumbnail visualization. |
| **Level 8** | **(570, 363)** | **256.0x (Min)** | Whole-slide overview and Tissue Masking generation. |

> 💡 **Data Scale Insight:** A single slide at Level 0 contains approximately **13.5 Gigapixels** ($145,920 \times 92,928$). Processing the entire image at once in RAM is impossible, necessitating a patching approach.

---

## 🗂️ Filename Pattern Convention

WSI filenames follow a strict tokenized convention:
`TO26.1_{PatientID}_M.{AgeGender}_APA-MAPN-MAPM_WS0.__1A.ADR.{Stain}`

* **`TO26.1`**: Cohort / Study identifier.
* **`{PatientID}`**: Unique tracking token for the patient (e.g., `261785`).
* **`M.58Y`**: Patient demographics (`M`/`F` for Gender, followed by age in years).
* **`APA-MAPN-MAPM`**: Histopathological classification of the cortical lesions (HISTALDO classification).
* **`WS0.__1A.ADR`**: Internal hardware slide scanner metadata.
* **`{Stain}`**: Staining modality identifier (`HE` or `CYP11B2`).

---

## 🛠️ Environment & Toolkit Requirements

To inspect annotations visually, external software such as **ASAP (Automated Slide Analysis Platform)** is highly recommended. For Python programmatic manipulation, install the following dependencies:

```bash
# Install system-level OpenSlide binaries (required for python-openslide)
apt-get update -y && apt-get install -y openslide-tools

# Install core and auxiliary deep learning digital pathology libraries
pip install openslide-python histolab tiatoolbox patchify

```
example of usage *openslide*:

```python
slide_he = openslide.OpenSlide(file_he_to_extract)

# 8 is the thumbnail level (low resolution)
(l, w)= slide_he.level_dimensions[8]
ratio= slide_he.level_downsamples[8]
thumbnail_he = slide_he.get_thumbnail(size=(l, w))

plt.figure(figsize=(10, 10))
plt.imshow(thumbnail_he)
plt.title("Thumbnail WSI H&E")
plt.axis('off')
plt.show()

```

---

## ⚙️ Core Extraction & Helper Functions

### 1. Filename Parser (Decryption)

This function automatically parses the complex file names into structured Python dictionaries to build clean metadata dataframes:

```python
def decript_filename_training(filename):
    ...
    return {
        'patient_id': patient_id,
        'gender': patient_gender,
        'age': patient_age,
        'study_id': study_id,
        'metadata': metadata,
        'stain': stain
    }

