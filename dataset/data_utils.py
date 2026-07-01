import openslide
import os
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np

def open_wsi(wsi_path: str) -> openslide.OpenSlide:
    """
    Apre in modo sicuro un file WSI (.ndpi, .svs, ecc.) tramite OpenSlide.
    """
    if not os.path.exists(wsi_path):
        raise FileNotFoundError(f"Impossibile trovare la WSI al percorso: {wsi_path}")
    return openslide.OpenSlide(wsi_path)

def get_wsi_level_info(slide: openslide.OpenSlide, level: int):
    """
    Restituisce le dimensioni e il fattore di downsample per uno specifico livello.
    Garantisce che il livello richiesto sia effettivamente presente nella piramide.
    """
    total_levels = slide.level_count
    if level < 0 or level >= total_levels:
        raise ValueError(f"Livello {level} non valido. La slide ha {total_levels} livelli (da 0 a {total_levels-1}).")
    
    dimensions = slide.level_dimensions[level]
    downsample = slide.level_downsamples[level]
    return dimensions, downsample

def get_wsi_thumbnail(slide: openslide.OpenSlide) -> Image.Image:
    """
    Genera una miniatura (thumbnail) leggera mantenendo il rapporto d'aspetto,
    ideale per visualizzazioni rapide e calcolo delle maschere di tessuto.
    """
    max_size= slide.level_dimensions[8]
    return slide.get_thumbnail(size=max_size)

def plot_wsi_thumbnail(slide: openslide.OpenSlide, title: str = "WSI Thumbnail"):
    """
    Mostra a schermo l’anteprima della WSI usando matplotlib.
    """
    thumbnail = get_wsi_thumbnail(slide)
    plt.figure(figsize=(8, 8))
    plt.imshow(thumbnail)
    plt.title(title)
    plt.axis('off')
    plt.show()


def extract_patch(slide: openslide.OpenSlide, x_0: int, y_0: int, patch_size: tuple = (256, 256), level: int = 0) -> Image.Image:
    """
    Estrae un patch (regione) a partire dalle coordinate (x_0, y_0) riferite al Livello 0.
    Converte automaticamente l'output da RGBA a RGB.
    """
    # get_wsi_level_info viene chiamata internamente per validare il livello
    _, _ = get_wsi_level_info(slide, level)
    
    # read_region restituisce un oggetto PIL in modalità RGBA
    patch = slide.read_region((x_0, y_0), level, patch_size)
    return patch.convert("RGB")

def plot_patches_comparison(patch_list: list, titles: list, figsize: tuple = (12, 4)):
    """
    Visualizza una riga di immagini/patch affiancate (es. H&E, CYP11B2, Maschera GT).
    
    Parametri:
    - patch_list: lista di oggetti PIL Image o array numpy da mostrare.
    - titles: lista di stringhe con i rispettivi titoli.
    """
    if len(patch_list) != len(titles):
        raise ValueError("La lista delle patch e quella dei titoli devono avere la stessa lunghezza.")
        
    num_images = len(patch_list)
    fig, axes = plt.subplots(1, num_images, figsize=figsize)
    
    # Se c'è solo un'immagine, axes non è una lista
    if num_images == 1:
        axes = [axes]
        
    for i, (img, title) in enumerate(zip(patch_list, titles)):
        # Se l'immagine è una maschera binaria (2D), usa la mappa di colore gray
        if isinstance(img, np.ndarray) and len(img.shape) == 2:
            axes[i].imshow(img, cmap='gray')
        else:
            axes[i].imshow(img)
            
        axes[i].set_title(title)
        axes[i].axis('off')
        
    plt.tight_layout()
    plt.show()

def decrypt_filename_training ( filename ):

    """
    Decrypts the filename to extract patient and study information.  
    Args:
        filename (str): The filename to decrypt.
    Returns:
        dict: A dictionary containing patient and study information.
            - 'patient_id': The patient ID.
            - 'gender': The patient's gender.
            - 'age': The patient's age.
            - 'study_id': The study ID.
            - 'metadata': The metadata.
            - 'stain': The stain.
    """
    file_name_parts= filename.split("_")

    parts=len(file_name_parts)
    if parts != 8:
        print (f"[WARNING] bad filename {parts} instead of 8")
        print (file_name_parts)
    study_id= file_name_parts[0]
    patient_id= file_name_parts[1]
    patient_gen_and_age= file_name_parts[2]

    patient_gender= patient_gen_and_age.split(".")[0]
    patient_age= patient_gen_and_age.split(".")[1]
    metadata_and_stain=file_name_parts[6]
    metadata_parts= metadata_and_stain.split(".")
    if len(metadata_parts)<3:
        metadata=  metadata_parts[0].replace("ADR", "")
        stain= metadata_parts[1]
    else:
        metadata=  metadata_parts[0]
        stain=  metadata_parts[2]

    p= {
        'patient_id': patient_id,
        'gender': patient_gender,
        'age': patient_age,
        'study_id': study_id,
        'metadata' : metadata,
        'stain': stain
    }
    return p

def encrypt_filename_training(obj):
    """
    Encrypts the patient and study information into a filename.
    Args:
        obj (dict): A dictionary containing patient and study information.
            - 'study_id': The study ID.
            - 'patient_id': The patient ID.
            - 'gender': The patient's gender.
            - 'age': The patient's age.
            - 'stain': The stain.
    Returns:
        tuple: A tuple containing two possible filenames.
    """
    filename= obj.get("study_id") + "_" + obj.get("patient_id")+"_"+obj.get("gender")+"."+obj.get("age")+"_"+"APA-MAPN-MAPMWS0.__"
    # due versioni con . e senza 
    stain= obj.get("stain")
    filename_1= filename+".ADR."+ stain +"_.ndpi"
    filename_2= filename+"ADR."+ stain +"_.ndpi"
    return filename_1, filename_2


def decrypt_filename_gt ( filename ):
    file_name_parts= filename.split("_")

    parts=len(file_name_parts)
    if parts != 9:
        print (f"[WARNING] bad filename {parts} instead of 9")
        print (file_name_parts)
    study_id= file_name_parts[0]
    patient_id= file_name_parts[1]
    patient_gen_and_age= file_name_parts[2]

    patient_gender= patient_gen_and_age.split(".")[0]
    patient_age= patient_gen_and_age.split(".")[1]
    metadata_and_stain=file_name_parts[6]
    metadata_parts= metadata_and_stain.split(".")
    
    gt_type= file_name_parts[8].split(".")[0]
    
    if len(metadata_parts)<3:
        metadata=  metadata_parts[0].replace("ADR", "")
        stain= metadata_parts[1]
    else:
        metadata=  metadata_parts[0]
        stain=  metadata_parts[2]

    p= {
        'patient_id': patient_id,
        'gender': patient_gender,
        'age': patient_age,
        'study_id': study_id,
        'metadata' : metadata,
        'stain': stain,
        'gt_type' : gt_type
    }
    return p

def encrypt_filename_gt(obj):
   pass