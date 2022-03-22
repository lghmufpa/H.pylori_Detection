#!/usr/bin/env python
# coding: utf-8

# In[2]:


# Fazer uma estratégia de salvamento que salve os resultos em pastas com timestamp

def proportional_sample(path_from_images, sample_percent):
    '''Function to select a proportional sample of labeled and unlabeled images
    from the total dataset
    
    Recieves:
    path_from_images = Path to the folder where the images are stored;
    train_percent = Proportion of the total data to be sampled.
    
    Retruns:
    total_sample_list = List of the selected images
    '''
    
    path_from_labels = '/'.join(path_from_images.split('/')[:-1])+'/labels'
    label_list = os.listdir(path_from_labels)
    
    positive_samples = random.sample(label_list, round(len(label_list)*sample_percent))
    positive_samples = [sample.split('.')[0]+'.tiff' for sample in positive_samples]    

    image_list = os.listdir(path_from_images)

    img_names = [img.split('.')[0] for img in image_list]
    label_names = [label.split('.')[0] for label in label_list]

    negative_cases = [name for name in img_names if name not in label_names]
    negative_samples_n = round((len(positive_samples)*len(image_list))/len(label_list))
    negative_samples = random.sample(negative_cases,negative_samples_n)
    negative_samples = [sample+'.tiff' for sample in negative_samples]
    
    total_sample_list = negative_samples + positive_samples
    random.shuffle(total_sample_list)
    
    return total_sample_list

def train_test_split(path_from, dataset, train_percent):
    '''Function to split the dataset into train and validation sets.
    
    Receives:
    path_from = Path to the folder where the images are stored;
    dataset = List of images available to be split into train and validation sets
    train_percent = Proportion of the data that will be used for training (default is 70%).
    
    Returns:
    train_list = List containing the images for training;
    valid_list = List containing the images for validation.'''
    
    train_list = random.sample(dataset, round(len(dataset)*train_percent))
    valid_list = [file for file in dataset if file not in train_list]
    
    train_list = [path_from+'/'+img for img in train_list]
    valid_list = [path_from+'/'+img for img in valid_list]
    
    return train_list, valid_list

def edit_hyp(working_dir,lr,gm,wd):
    '''Function to read the base hyperparameter file and write a new yaml file,
    altering the initial learning rate, the wheight decay and the gradient momentum
    of the original one.
    
    Recieves:
    working_dir = The direcory containing the YOLOv3 configuration;
    lr = learning rate (float);
    gm = gradiente momentum (float);
    wd = wheight decay (float).
    
    Returns nothing'''
    
    #Getting the base hyperparameter file
    yaml_file = working_dir + '/data/hyp.scratch.yaml'
    
    #Altering the selected hyperparameters
    with open(yaml_file) as file:
        documents = yaml.full_load(file)
        for item, doc in documents.items():
            if item == 'lr0':
                documents[item] = lr #initial learning rate
                documents['lrf'] = 20*lr #final learning rate
            if item == 'momentum':
                documents[item] = gm
            if item == 'weight_decay':
                documents[item] = wd
    
    #Writing the new hyperparameter file
    new_hyp_file = working_dir + '/data/hyp.mod.yaml'
    with open(new_hyp_file, 'w') as file:
        documents = yaml.dump(documents, file)
        
    return

def edit_yaml(yaml_file,path_to):
    '''Function to edit the .yaml file containing the traind and valid paths
    and save it on top of the original one.
    
    Receives:
    yaml_file = .yaml file that contains the number of classes, it's names and paths to training and validation sets;
    path_to = path were the text files containing the train and validation lists are stored.
    
    Retruns nothing.'''

    with open(yaml_file) as file:
        documents = yaml.full_load(file)

        for item, doc in documents.items():
            if item == 'train':
                documents[item] = path_to+'/images_train.txt'
            if item == 'val':
                documents[item] = path_to+'/images_valid.txt'
                
    with open(yaml_file, 'w') as file:
        documents = yaml.dump(documents, file)
    
    return

def write_file(path_to, train, valid):
    '''Function to write the files containing the train and validation image lists.
    
    Receives:
    path_to = Path were the text files will be saved;
    train = List containing the images for training;
    valid = List containing the images for validation;
    yaml_file = .yaml file that contains the number of classes, it's names and paths to training and validation sets.
    
    Calls the edit_yaml function at the end
    
    Retruns nothing.'''
    
    with open(path_to+'/images_train.txt', "w") as saida:
        for linha in [train]:
            linha = '\n'.join(linha)
            saida.write(linha)
        
    with open(path_to+'/images_valid.txt', "w") as saida:
        for linha in [valid]:
            linha = '\n'.join(linha)
            saida.write(linha)
    
    return

def metric_mean(path_to_runs,path_to_save,epochs,rep):
    '''Function to calculate the mean of the metrics obtained in the cross-validation
    and write the file the mean of the evaluation metrics.
    
    Receives:
    path_to_runs = Path to where the run folders generated by the execution of YOLO are stored;
    path_to_save = Path to where the file containing the mean of the metrics will be saved;
    rep = Number of repetitions applied in the cross-validation.
    
    Returns:
    results_cross = List containing the mean of the metrics;
    header = List containing the name of the metrics.
    '''
    
    all_runs = list(os.listdir(path_to_runs))
    all_runs = natsorted(all_runs)
    recent_runs = all_runs[-rep:]

    results_cross = np.zeros((epochs,rep)).tolist()
    for folder in recent_runs:
        results_temp = []
        for file in os.listdir(path_to_runs + '/' + folder):
            if file == 'results.txt':
                with open(path_to_runs + '/' + folder + '/' + file) as results:
                    content = results.readlines()
                    for line in content:
                        line = line.strip('\n')
                        line = line.split(' ')
                        line = [x for x in line if x != '']
                        new_line = list(map(line.__getitem__, [2,3,4,8,9,10,11,12,13,14]))
                        results_temp.append(new_line)

        for i, line in enumerate(results_temp):
            for j,element in enumerate(line):
                results_cross[i][j] = results_cross[i][j] + float(element)

    for i,line in enumerate(results_cross):
        results_cross[i] = [x/rep for x in line]

    with open(path_to_save+'/results_cross_validation.txt', "w") as output:
        header = ['train_box_loss','train_objectness_loss','train_classificaion_loss','precision','recall','mAP_0.5','mAP_0.5:0.95','val_box_loss','val_objectness_loss','val_classificaion_loss']
        header = '\t'.join(header)
        header = header + '\n'
        output.write(header)
        for line in results_cross:
            line = [str(x) for x in line]
            line = '\t'.join(line)
            line = line + '\n'
            output.write(line)
    
    return results_cross, header

def metric_plots(path_to_results,metrics_cv, header):
    '''Function to generate the line plot of the mean of the metrics.
    
    Receives:
    path_to_results = Path to were the images are going to be saved;
    metrics_cv = List containing the mean of the metrics;
    header = List containing the name of the metrics.
    
    Returns nothing.
    '''
    plt.style.use('seaborn-whitegrid')
    
    header = ['train_box_loss','train_objectness_loss','train_classificaion_loss','precision','recall','mAP_0.5','mAP_0.5:0.95','val_box_loss','val_objectness_loss','val_classificaion_loss']

    df = pd.DataFrame(metrics_cv, columns = header)
    for metric in header:
        title = metric.split('_')
        title = ' '.join(title)
        title = title + ' cross-validation'
        title_file = title.split(' ')
        title_file = '_'.join(title_file)

        plt.plot(df[metric],'k-')
        plt.title(title,fontdict = {'size': 16, 'color': 'black'})
        plt.xlabel('epochs',fontdict = {'size': 12, 'color': 'black'})
        plt.ylabel(metric, fontdict = {'size': 12, 'color': 'black'})
        plt.savefig(path_to_results + '/' + title_file + '.png',dpi=400)
        plt.figure()

    return

def main_flux(working_dir,path_from_imgs, path_to, yaml_file, rep, command):
    '''Function containing the main flux of the training with the standard hyperparameters.
    
    Recieves:
    working_dir = Directory containing the train.py file;
    path_from_imgs = Path where the images are stored;
    path_to_results = Path where the text file containing the mean of the metrics and the line plot of them will be saved;
    yaml_file = .yaml file that contains the number of classes, it's names and paths to training and validation sets;
    rep = Number of repetitions applied in the cross-validation.
    command = String containing the command for the YOLOv3
    
    Retruns nothing'''
    
    os.chdir(working_dir)
    
    #Creation of the unique directory for this run
    ts = datetime.datetime.now().timestamp() 
    ts = int(ts) 
    path_to = path_to + '/results_' + str(ts)
    os.mkdir(path_to)
    
    #Path to where the run folders generated by the execution of YOLO are stored;
    path_to_runs = working_dir + '/runs/train' 
    
    #Path where the text files containing the list of train and validation images will be saved;
    path_to_train_valid = os.path.dirname(path_from_imgs)
    
    #Edit the 'val' and 'train' paths in the yaml configuration file
    edit_yaml(yaml_file,path_to_train_valid)
    
    lr_list = [0.1,0.01,0.001,0.0001,0.00001] #learning rate list
    gm_list = [0.99,0.975,0.95,0.925,0.9] #gradient momentum list
    wd_list = [0.05,0.005,0.0005,0.00005,0.000005] #wheight decay list
    
    for lr in lr_list:
        for gm in gm_list:
            for wd in wd_list:
                image_list = proportional_sample(path_from_imgs,0.5)
                edit_hyp(working_dir,lr,gm,wd)
                #Creation of the directory that will contain the results for this set of hyperparameter
                path_to_results = path_to + '/results_' + str(lr) + '_' + str(gm) + '_' + str(wd)
                os.mkdir(path_to_results)
                for i in range(rep):
                    train, valid = train_test_split(path_from_imgs,image_list, 0.7)
                    write_file(path_to_train_valid,train,valid)
                    os.system(command)
    
                metrics_cv, header = metric_mean(path_to_runs,path_to_results,30,rep)
                metric_plots(path_to_results,metrics_cv, header)
    
    return

if __name__ == '__main__':
    
    '''Main execution block, imports the libraries and gets the parameters to the
    main_flux function'''
    
    import os
    import sys
    import random
    import numpy as np
    import pandas as pd 
    from natsort import natsorted
    import yaml
    import matplotlib.pyplot as plt
    import datetime 
    
    working_dir = sys.argv[1]
    path_from_imgs = sys.argv[2]
    path_to_results = sys.argv[3]
    yaml_file = sys.argv[4]
    rep = int(sys.argv[5])
    command = sys.argv[6]
    
    main_flux(working_dir,path_from_imgs, path_to_results, yaml_file, rep, command)

#https://medium.com/data-hackers/como-criar-k-fold-cross-validation-na-m%C3%A3o-em-python-c0bb06074b6b

#https://machinelearningmastery.com/implement-resampling-methods-scratch-python/


# In[23]:




