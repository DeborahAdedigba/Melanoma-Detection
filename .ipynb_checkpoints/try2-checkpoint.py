import streamlit as st
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.vgg16 import preprocess_input as preprocess_vgg16
from tensorflow.keras.applications.resnet50 import preprocess_input as preprocess_resnet50
from tensorflow.keras.applications.efficientnet import preprocess_input as preprocess_efficientnet
from tensorflow.keras.applications.inception_resnet_v2 import preprocess_input as preprocess_inceptionresnetv2
import matplotlib.pyplot as plt
from io import StringIO
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Conv2D, MaxPooling2D, Dropout, Flatten, Dense, BatchNormalization
from tensorflow.keras.regularizers import l2
from tensorflow.keras.layers import Dense, Dropout, GlobalAveragePooling2D, concatenate
from tensorflow.keras.applications import VGG16, ResNet50, InceptionResNetV2, EfficientNetB4
import pandas as pd
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go


# CNN
def build_model(input_shape=(224, 224, 6)):  # 6 channels for image + saliency
    inputs = Input(input_shape)
    image_input = inputs[:, :, :, :3]
    saliency_input = inputs[:, :, :, 3:]

    def create_cnn(input_tensor):
        conv1 = Conv2D(32, (3, 3), activation='relu', padding='same', kernel_regularizer=l2(0.01))(input_tensor)
        conv1 = BatchNormalization()(conv1)
        conv1 = Conv2D(32, (3, 3), activation='relu', padding='same', kernel_regularizer=l2(0.01))(conv1)
        conv1 = BatchNormalization()(conv1)
        pool1 = MaxPooling2D(pool_size=(2, 2))(conv1)
        pool1 = Dropout(0.5)(pool1)
        conv2 = Conv2D(64, (3, 3), activation='relu', padding='same', kernel_regularizer=l2(0.01))(pool1)
        conv2 = BatchNormalization()(conv2)
        conv2 = Conv2D(64, (3, 3), activation='relu', padding='same', kernel_regularizer=l2(0.01))(conv2)
        conv2 = BatchNormalization()(conv2)
        pool2 = MaxPooling2D(pool_size=(2, 2))(conv2)
        pool2 = Dropout(0.5)(pool2)
        conv3 = Conv2D(128, (3, 3), activation='relu', padding='same', kernel_regularizer=l2(0.01))(pool2)
        conv3 = BatchNormalization()(conv3)
        conv3 = Conv2D(128, (3, 3), activation='relu', padding='same', kernel_regularizer=l2(0.01))(conv3)
        conv3 = BatchNormalization()(conv3)
        pool3 = MaxPooling2D(pool_size=(2, 2))(conv3)
        pool3 = Dropout(0.5)(pool3)
        conv4 = Conv2D(256, (3, 3), activation='relu', padding='same', kernel_regularizer=l2(0.01))(pool3)
        conv4 = BatchNormalization()(conv4)
        conv4 = Conv2D(256, (3, 3), activation='relu', padding='same', kernel_regularizer=l2(0.01))(conv4)
        conv4 = BatchNormalization()(conv4)
        pool4 = MaxPooling2D(pool_size=(2, 2))(conv4)
        pool4 = Dropout(0.5)(pool4)
        conv5 = Conv2D(512, (3, 3), activation='relu', padding='same', kernel_regularizer=l2(0.01))(pool4)
        conv5 = BatchNormalization()(conv5)
        conv5 = Conv2D(512, (3, 3), activation='relu', padding='same', kernel_regularizer=l2(0.01))(conv5)
        conv5 = BatchNormalization()(conv5)
        pool5 = MaxPooling2D(pool_size=(2, 2))(conv5)
        pool5 = Dropout(0.5)(pool5)
        flatten = Flatten()(pool5)
        return flatten

    image_features = create_cnn(image_input)
    saliency_features = create_cnn(saliency_input)
    concatenated_features = tf.keras.layers.Concatenate()([image_features, saliency_features])
    dense1 = Dense(256, activation='relu', kernel_regularizer=l2(0.01))(concatenated_features)
    dense1 = Dropout(0.5)(dense1)
    output = Dense(6, activation='softmax')(dense1)

    model = Model(inputs=inputs, outputs=output)
    return model

# EfficientB4
def build_model_with_saliency_Eff(input_shape=(380, 380, 6), num_classes=6):
    base_model = EfficientNetB4(include_top=False, weights=None, input_shape=(380, 380, 3))

    # Split the input into image and saliency map
    inputs = Input(input_shape)
    image_input = inputs[:, :, :, :3]
    saliency_input = inputs[:, :, :, 3:]

    # Process the image input
    x = base_model(image_input, training=False)
    x = GlobalAveragePooling2D()(x)

    # Process the saliency map
    y = base_model(saliency_input, training=False)
    y = GlobalAveragePooling2D()(y)

    # Combine both processed inputs
    combined = concatenate([x, y])
    combined = Dense(256, activation='relu')(combined)
    combined = Dropout(0.5)(combined)
    output = Dense(num_classes, activation='softmax')(combined)

    model = Model(inputs=inputs, outputs=output)
    return model

# VGG16


def build_model_with_saliency_Vgg(input_shape=(224, 224, 6), weights_path=None, num_classes=6):
    base_model = VGG16(include_top=False, weights=None, input_shape=(224, 224, 3))
    if weights_path is not None:
        base_model.load_weights(weights_path, by_name=True)
    base_model.trainable = False  # Freeze the base model

    # Split the input into image and saliency map
    inputs = Input(input_shape)
    image_input = inputs[:, :, :, :3]
    saliency_input = inputs[:, :, :, 3:]

    # Process the image input
    x = base_model(image_input, training=False)
    x = GlobalAveragePooling2D()(x)

    # Process the saliency map
    y = base_model(saliency_input, training=False)
    y = GlobalAveragePooling2D()(y)

    # Combine both processed inputs
    combined = concatenate([x, y])
    combined = Dense(256, activation='relu')(combined)
    combined = Dropout(0.5)(combined)
    output = Dense(num_classes, activation='softmax')(combined)

    model = Model(inputs=inputs, outputs=output)
    return model

#Resnet50
def build_model_with_saliency_Res(input_shape=(224, 224, 6), num_classes=6):
    base_model = ResNet50(include_top=False, weights=None, input_shape=(224, 224, 3))

    # Split the input into image and saliency map
    inputs = Input(input_shape)
    image_input = inputs[:, :, :, :3]
    saliency_input = inputs[:, :, :, 3:]

    # Process the image input
    x = base_model(image_input, training=False)
    x = GlobalAveragePooling2D()(x)

    # Process the saliency map
    y = base_model(saliency_input, training=False)
    y = GlobalAveragePooling2D()(y)

    # Combine both processed inputs
    combined = concatenate([x, y])
    combined = Dense(256, activation='relu')(combined)
    combined = Dropout(0.5)(combined)
    output = Dense(num_classes, activation='softmax')(combined)

    model = Model(inputs=inputs, outputs=output)
    return model

# InceptionResNetV2


def build_model_with_saliency_Inc(input_shape=(299, 299, 6), num_classes=6):
    base_model = InceptionResNetV2(include_top=False, weights=None, input_shape=(299, 299, 3))

    # Split the input into image and saliency map
    inputs = Input(input_shape)
    image_input = inputs[:, :, :, :3]
    saliency_input = inputs[:, :, :, 3:]

    # Process the image input
    x = base_model(image_input, training=False)
    x = GlobalAveragePooling2D()(x)

    # Process the saliency map
    y = base_model(saliency_input, training=False)
    y = GlobalAveragePooling2D()(y)

    # Combine both processed inputs
    combined = concatenate([x, y])
    combined = Dense(256, activation='relu')(combined)
    combined = Dropout(0.5)(combined)
    output = Dense(num_classes, activation='softmax')(combined)

    model = Model(inputs=inputs, outputs=output)
    return model




# Define class labels for multi-class classification
skin_labels = ['ACK', 'BCC', 'MEL', 'NEV', 'SCC', 'SEK']

def load_models():
    models = {
        'skin': {},
        'derm': {}
    }

    # Load dermoscopy image models
    try:
        model_derm_cnn = load_model('DM_melanoma_cnn_with_saliency.keras')
        model_derm_vgg16 = load_model('DM_vgg16_model_with_saliency.keras')
        model_derm_resnet50 = load_model('DM_best_ResNet50_model.keras')
        model_derm_efficientnet = load_model('DM_efficientnetb4_model_with_saliency.keras')
        model_derm_inceptionresnetv2 = load_model('DM_InceptionResNetV2_model.keras')
    except Exception as e:
        st.error(f"Error loading dermoscopy image models: {e}")

    # Load skin image models
    try:
        # Load the CNN model weights
        model_skin_cnn = build_model()
        model_skin_cnn.load_weights('CNN_skin_classifier_weights.weights.h5')
        # st.write("Loaded CNN skin classifier model.")
    except Exception as e:
        st.error(f"Error loading CNN skin classifier model: {e}")

    try:
        # Load the VGG16 model weights
        model_skin_vgg16 = build_model_with_saliency_Vgg(input_shape=(224, 224, 6), num_classes=6)
        model_skin_vgg16.load_weights('best_VGG16_weights.weights.h5')
        # st.write("VGG16 skin model loaded successfully.")
    except Exception as e:
        st.error(f"Error loading VGG16 skin model: {e}")

    try:
        # Load the ResNet50 model weights
        model_skin_resnet50 = build_model_with_saliency_Res(input_shape=(224, 224, 6), num_classes=6)
        model_skin_resnet50.load_weights('best_ResNet50_weights.weights.h5')
        # st.write("ResNet50 skin model loaded successfully.")
    except Exception as e:
        st.error(f"Error loading ResNet50 skin model: {e}")

    try:
        # Load the EfficientNetB4 model weights
        model_skin_efficientnet = build_model_with_saliency_Eff(input_shape=(380, 380, 6), num_classes=6)
        model_skin_efficientnet.load_weights('best_EfficientNetB4_weights.weights.h5')
        # st.write("EfficientNetB4 skin model loaded successfully.")
    except Exception as e:
        st.error(f"Error loading EfficientNetB4 skin model: {e}")

    try:
        # Load the InceptionResNetV2 model weights
        model_skin_inceptionresnetv2 = build_model_with_saliency_Inc(input_shape=(299, 299, 6), num_classes=6)
        model_skin_inceptionresnetv2.load_weights('best_InceptionResNetV2_weights.weights.h5')
        # st.write("InceptionResNetV2 skin model loaded successfully.")
    except Exception as e:
        st.error(f"Error loading InceptionResNetV2 skin model: {e}")

    return {
        'derm': {
            'CNN': model_derm_cnn,
            'VGG16': model_derm_vgg16,
            'ResNet50': model_derm_resnet50,
            'EfficientNetB4': model_derm_efficientnet,
            'InceptionResNetV2': model_derm_inceptionresnetv2
        },
        'skin': {
            'CNN': model_skin_cnn,
            'VGG16': model_skin_vgg16,
            'ResNet50': model_skin_resnet50,
            'EfficientNetB4': model_skin_efficientnet,
            'InceptionResNetV2': model_skin_inceptionresnetv2
        }
    }, model_skin_cnn, model_skin_vgg16, model_skin_resnet50, model_skin_efficientnet, model_skin_inceptionresnetv2

def melanoma_detection():
    st.title('Melanoma Detection')

    # Model selection
    st.sidebar.title('Model Selection')
    model_type = st.sidebar.radio('Select Model Type', ['Skin Image Models', 'Dermoscopy Image Models'])
    
    loaded_models, model_skin_cnn, model_skin_vgg16, model_skin_resnet50, model_skin_efficientnet, model_skin_inceptionresnetv2 = load_models()

    if model_type == 'Skin Image Models':
        models = ['CNN', 'VGG16', 'ResNet50', 'EfficientNetB4', 'InceptionResNetV2']
        model_dict = {
            'CNN': model_skin_cnn,
            'VGG16': model_skin_vgg16,
            'ResNet50': model_skin_resnet50,
            'EfficientNetB4': model_skin_efficientnet,
            'InceptionResNetV2': model_skin_inceptionresnetv2
        }
        preprocess_dict = {
            'VGG16': preprocess_vgg16,
            'ResNet50': preprocess_resnet50,
            'EfficientNetB4': preprocess_efficientnet,
            'InceptionResNetV2': preprocess_inceptionresnetv2
        }
    else:  # Dermoscopy Image Models
        models = ['CNN', 'VGG16', 'ResNet50', 'EfficientNetB4', 'InceptionResNetV2']
        model_dict = loaded_models['derm']
        preprocess_dict = {
            'VGG16': preprocess_vgg16,
            'ResNet50': preprocess_resnet50,
            'EfficientNetB4': preprocess_efficientnet,
            'InceptionResNetV2': preprocess_inceptionresnetv2
        }

    selected_model = st.sidebar.selectbox('Select Model', models)

    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        st.image(uploaded_file, caption='Uploaded Image.', use_column_width=True)
        st.write("")
        st.write("Classifying...")

        try:
            # Determine input size based on the selected model
            if selected_model == 'EfficientNetB4':
                input_size = (380, 380)
            elif selected_model == 'InceptionResNetV2':
                input_size = (299, 299)
            else:
                input_size = (224, 224)

            # Process uploaded image
            img = image.load_img(uploaded_file, target_size=input_size)
            img = image.img_to_array(img)
            img = np.expand_dims(img, axis=0)

            # Preprocess based on model
            if selected_model in preprocess_dict:
                img = preprocess_dict[selected_model](img)

            # Assuming saliency map is generated (dummy saliency map for illustration)
            saliency_map = np.zeros_like(img)

            # Concatenate the original image with the saliency map
            combined_input = np.concatenate((img, saliency_map), axis=-1)

            # Model prediction
            model = model_dict.get(selected_model)
            if model is None:
                st.error("Selected model is not available.")
            else:
                prediction = model.predict(combined_input)

                # Handle the prediction output
                if model_type == 'Skin Image Models':  # Multi-class output for skin images
                    predicted_class = np.argmax(prediction, axis=-1)
                    confidence = np.max(prediction)
                    result = skin_labels[predicted_class[0]]
                else:  # Binary output for dermoscopy images
                    threshold = 0.5  # Adjust this threshold as needed
                    predicted_class = (prediction[:, 0] > threshold).astype(int)
                    confidence = prediction[0, 0]
                    result = 'Malignant' if predicted_class[0] == 1 else 'Benign'

                st.write(f"Prediction: {result}")
                st.write(f"Confidence: {confidence:.2f}")

                # Additional information
                st.write("\nPlease note:")
                st.write("- This prediction is based on the model's analysis and should not be considered as a definitive medical diagnosis.")
                st.write("- If you have any concerns about a skin lesion, please consult with a qualified healthcare professional or dermatologist.")
                st.write("- Regular skin check-ups and early detection are crucial for managing melanoma risk.")

        except Exception as e:
            st.error(f"Error during prediction: {e}")
    else:
        st.write("Please upload an image.")


# Disclaimer text
disclaimer_text = """
**Disclaimer:** This app is for educational purposes only. Consult a healthcare professional for accurate medical advice.
"""

# Main page - Introduction about Melanoma and the App
def main():
    st.title('Melanoma Detection App')
    st.markdown("""
        ## Welcome to the Melanoma Detection App!

        This app is designed to help you understand and detect melanoma, a type of skin cancer. Melanoma is the most serious form of skin cancer and can be life-threatening if not detected and treated early.

        Using the latest advancements in deep learning and computer vision, this app provides a platform to explore different models for melanoma detection, visualize and analyze relevant data, and learn more about this important health topic.

        The key features of this app include:

        - **Model Selection and Performance**: Explore the accuracy, precision, recall, and AUC of various models for both skin and dermoscopy image classification.
        - **Visualizations**: Analyze the distribution of melanoma cases, age, and gender using interactive visualizations.
        - **Melanoma Detection**: Upload your own skin or dermoscopy images and get a prediction on whether the lesion is malignant or benign.
        - **Educational Resources**: Access a curated list of articles, journals, and websites to deepen your understanding of melanoma and related technologies.
        - **FAQs**: Get answers to common questions about the app, its models, and interpreting the results.
        - **Feedback and Contact**: Provide feedback or reach out to the app developers for support.

        We hope this app will be a valuable resource in your journey to learn about and detect melanoma. Let's get started!
    """)



def display_model_summaries(models):
    for category, category_models in models.items():
        st.header(f"{category.capitalize()} Models")
        st.write("This section provides a detailed summary of the selected model's architecture, including the number of layers, parameters, and output shapes.")
        for model_name, model in category_models.items():
            st.subheader(f"{model_name} Model Summary")
            summary_string = StringIO()
            model.summary(print_fn=lambda x: summary_string.write(x + '\n'))
            st.text(summary_string.getvalue())
            st.markdown("---")


# Function to display model evaluation metrics
def display_model_evaluation(metrics, model_type, model_name):
    if model_name in metrics:
        st.write(f"### Model Performance for {model_name} ({model_type})")
        st.write("The following metrics provide an overview of the selected model's performance:")
        st.write(f"**Accuracy**: {metrics[model_name]['Accuracy']}")
        st.write(f"**Precision**: {metrics[model_name]['Precision']}")
        st.write(f"**Recall**: {metrics[model_name]['Recall']}")
        st.write(f"**AUC**: {metrics[model_name]['AUC']}")
    else:
        st.write("Metrics not available.")

# Function to display confusion matrix
def display_confusion_matrix(confusion_matrices, model_type, model_name):
    matrix = confusion_matrices.get(model_type, {}).get(model_name)
    if matrix is not None:
        if model_type == 'dermoscopy':
            labels = ['Benign', 'Malignant']
        else:  # Skin Image Models
            labels = ['ACK', 'BCC', 'MEL', 'NEV', 'SCC', 'SEK']
        
        df_cm = pd.DataFrame(matrix, index=labels, columns=labels)
        plt.figure(figsize=(8, 6))
        sns.heatmap(df_cm, annot=True, fmt='d', cmap='Blues')
        plt.title(f'Confusion Matrix for {model_name} ({model_type.capitalize()})')
        plt.ylabel('Actual')
        plt.xlabel('Predicted')
        st.pyplot(plt)

        st.write(f"The confusion matrix above shows the performance of the {model_name} model for {model_type.capitalize()} classification.")
        st.write(f"The diagonal elements represent the number of correct predictions, while the off-diagonals represent the number of incorrect predictions.")
    else:
        st.write(f"No confusion matrix available for {model_name} in {model_type}.")

# Confusion matrices for models
confusion_matrices = {
    'dermoscopy': {
        'VGG16': [[94, 42], [34, 121]],
        'ResNet50': [[106, 30], [39, 116]],
        'EfficientNetB4': [[119, 17], [26, 129]],
        'InceptionResNetV2': [[59, 77], [30, 125]],
        'CNN': [[84, 52], [51, 104]]
    },
    'skin': {
        'EfficientNetB4': [[110, 36, 4, 9, 18, 5],
                           [30, 101, 1, 10, 16, 4],
                           [5, 0, 123, 15, 6, 4],
                           [3, 9, 12, 117, 5, 14],
                           [19, 28, 17, 13, 86, 25],
                           [18, 13, 13, 26, 12, 87]],

        'VGG16': [[112, 32, 2, 2, 24, 10],
                  [27, 103, 1, 5, 17, 9],
                  [0, 0, 144, 0, 0, 9],
                  [5, 3, 1, 138, 6, 7],
                  [22, 38, 0, 1, 117, 10],
                  [21, 8, 5, 7, 3, 125]],

        'ResNet50': [[134, 18, 1, 3, 18, 8],
                     [23, 104, 3, 6, 24, 2],
                     [2, 0, 140, 6, 3, 2],
                     [1, 3, 1, 146, 2, 7],
                     [16, 27, 2, 0, 136, 7],
                     [16, 4, 0, 15, 0, 134]],

        'InceptionResNetV2': [[118, 24, 4, 4, 25, 7],
                              [25, 64, 2, 18, 30, 23],
                              [4, 0, 98, 38, 0, 13],
                              [2, 7, 13, 128, 0, 10],
                              [34, 37, 1, 10, 94, 12],
                              [27, 12, 13, 37, 8, 72]],

        'CNN': [[88, 55, 3, 1, 17, 18],
                [25, 125, 0, 3, 2, 7],
                [1, 1, 141, 8, 0, 2],
                [1, 0, 0, 153, 0, 6],
                [10, 3, 0, 0, 170, 5],
                [0, 0, 1, 5, 1, 162]]
    }
}

def display_selected_model_summary(models):
    image_type = st.sidebar.selectbox('Select Image Type', ['Skin', 'Dermoscopy'])
    model_key = 'skin' if image_type == 'Skin' else 'derm'
    
    model_name = st.sidebar.selectbox('Select Model', list(models[model_key].keys()))
    
    st.header(f"{image_type} - {model_name} Model Summary")
    model = models[model_key][model_name]
    summary_string = StringIO()
    model.summary(print_fn=lambda x: summary_string.write(x + '\n'))
    st.text(summary_string.getvalue())


# Main function to handle the model performance page

def model_performance_page():
    if 'models' not in st.session_state:
        loaded_data = load_models()
        st.session_state.models = loaded_data[0] if isinstance(loaded_data, tuple) else loaded_data
        
    st.title("Model Performance")
    st.markdown("This section allows you to explore the performance of various models used for melanoma detection. You can view the model summaries, evaluation metrics, and confusion matrices.")
    
    metrics_dermoscopy = {
        'CNN': {'Accuracy': '53%', 'Precision': '53%', 'Recall': '53%', 'AUC': '52%'},
        'VGG16': {'Accuracy': '74%', 'Precision': '74%', 'Recall': '74%', 'AUC': '83%'},
        'ResNet50': {'Accuracy': '75%', 'Precision': '75%', 'Recall': '75%', 'AUC': '84%'},
        'EfficientNetB4': {'Accuracy': '85%', 'Precision': '85%', 'Recall': '85%', 'AUC': '95%'},
        'InceptionResNetV2': {'Accuracy': '60%', 'Precision': '60%', 'Recall': '60%', 'AUC': '64%'}
    }
    metrics_skin = {
        'CNN': {'Accuracy': '75%', 'Precision': '95%', 'Recall': '44%', 'AUC': '96%'},
        'VGG16': {'Accuracy': '74%', 'Precision': '82%', 'Recall': '66%', 'AUC': '95%'},
        'ResNet50': {'Accuracy': '79%', 'Precision': '84%', 'Recall': '76%', 'AUC': '97%'},
        'EfficientNetB4': {'Accuracy': '61%', 'Precision': '70%', 'Recall': '50%', 'AUC': '89%'},
        'InceptionResNetV2': {'Accuracy': '57%', 'Precision': '95%', 'Recall': '44%', 'AUC': '96%'}
    }
    
    # Sidebar selection for viewing type
    view_type = st.sidebar.selectbox('Select View', ['Model Summary', 'Model Evaluation', 'Confusion Matrix'])
    
    if view_type == 'Model Summary':
        display_selected_model_summary(st.session_state.models)
    elif view_type == 'Model Evaluation':
        model_type = st.sidebar.selectbox('Select Model Type', ['Skin Image Models', 'Dermoscopy Image Models'])
        metrics = metrics_skin if model_type == 'Skin Image Models' else metrics_dermoscopy
        model_name = st.sidebar.selectbox('Select Model', list(metrics.keys()))
        display_model_evaluation(metrics, model_type, model_name)
    elif view_type == 'Confusion Matrix':
        model_type = st.sidebar.selectbox('Select Model Type', ['Skin Image Models', 'Dermoscopy Image Models'])
        model_type_key = 'skin' if model_type == 'Skin Image Models' else 'dermoscopy'
        model_name = st.sidebar.selectbox('Select Model', list(confusion_matrices[model_type_key].keys()))
        display_confusion_matrix(confusion_matrices, model_type_key, model_name)





# plotting the visualization from the metadata
def visualize_data():
    st.title('Visualizations')
    st.markdown("""
        ## Visualizations
        This section provides interactive visualizations to help you understand the distribution of melanoma cases, age, and gender in the dataset.
        
        You can switch between visualizations for skin images and dermoscopy images using the sidebar selection.
    """)

    # Load datasets
    df = pd.read_csv('C:/Users/adedi/OneDrive - Solent University/Diss/Dissertation/Dataset/Source_2/metadata.csv')
    df2 = pd.read_csv('C:/Users/adedi/OneDrive - Solent University/Diss/Dissertation/Dataset/Source_1_ISIC/ISBI2016_ISIC_Part3_Training_GroundTruth.csv')

    # Sidebar selection
    visualization_type = st.sidebar.selectbox('Select Visualization', ['Skin', 'Dermoscopy'])

    if visualization_type == 'Skin':
        # Skin Visualizations
        # Count plot for diagnostic
        plt.figure(figsize=(8, 6))
        sns.countplot(data=df, x='diagnostic')
        plt.title('Diagnostic Distribution for PH2 Dataset')
        plt.xlabel('Diagnostic')
        plt.ylabel('Count')

        # Annotate counts on bars
        for p in plt.gca().patches:
            plt.gca().annotate(f"{p.get_height()}", (p.get_x() + p.get_width() / 2., p.get_height()), ha='center', va='center', xytext=(0, 5), textcoords='offset points')
        st.pyplot(plt.gcf())

        # Count plot for gender
        plt.figure(figsize=(8, 6))
        sns.countplot(data=df, x='gender', hue='diagnostic')
        plt.title('Diagnostic Distribution by Gender for PH2 Dataset')
        plt.xlabel('Gender')
        plt.ylabel('Count')
        plt.legend(title='Diagnostic')

       
        # Annotate counts on bars
        for p in plt.gca().artists:
            p.set_edgecolor('k')  # set edge color for better visibility
            plt.gca().annotate(f"{p.get_height()}", (p.get_x() + p.get_width() / 2., p.get_height()), ha='center', va='center', xytext=(0, 5), textcoords='offset points')
        st.pyplot(plt.gcf())



        # Box plot for age by diagnostic
        fig = px.box(df, x='diagnostic', y='age', title='Age Distribution by Diagnostic for PH2 Dataset')
        st.plotly_chart(fig)

    elif visualization_type == 'Dermoscopy':
        # Dermoscopy Visualizations
        # Count plot for label
        plt.figure(figsize=(8, 6))
        sns.countplot(data=df2, x='Label', order=df2['Label'].value_counts().index)
        plt.title('Distribution of Labels for ISIC2016 Dataset')
        plt.xlabel('Label')
        plt.ylabel('Count')

        # Annotate counts on bars
        for p in plt.gca().patches:
            plt.gca().annotate(f"{p.get_height()}", (p.get_x() + p.get_width() / 2., p.get_height()), ha='center', va='center', xytext=(0, 5), textcoords='offset points')
        st.pyplot(plt.gcf())

        



# Educational resources section
def educational_resources():
    st.title('Educational Resources')
    st.markdown("""
        ## Educational Resources for Melanoma Detection
        
        In this section, you can find a curated list of resources to deepen your understanding of melanoma and the technologies used in this app for detection.
        
        The resources include academic articles, reputable websites, scientific journals, and research papers that cover various aspects of melanoma and deep learning for medical imaging.
        
        Feel free to explore these resources to learn more about this important health topic and the latest advancements in the field.
    """)

    st.markdown("""
        - [Melanoma Detection with Deep Learning](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6984940/): An academic article on using deep learning for melanoma detection.
        - [Skin Cancer Foundation](https://www.skincancer.org/): Comprehensive resource on skin cancer, including melanoma.
        - [Deep Learning for Dermatology](https://www.sciencedirect.com/science/article/pii/S0045653518300556): Review of deep learning techniques applied to dermatology.
        - [Journal of the American Academy of Dermatology (JAAD)](https://www.jaad.org/): Leading dermatology journal with articles on melanoma and skin diseases.
        - [Convolutional Neural Networks for Melanoma Detection](https://arxiv.org/abs/1805.06267): Research paper on applying CNNs for melanoma detection.
        - [ISIC Archive](https://www.isic-archive.com/): A large dataset of dermatological images for training and evaluation of models.
        - [Understanding Melanoma](https://www.cancer.gov/types/skin/melanoma): National Cancer Institute resource explaining melanoma and its treatment.
        - [AI for Melanoma Detection](https://www.bmj.com/content/369/bmj.m1972): Article discussing the use of AI in detecting melanoma.
    """)


# FAQs section
def faq_section():
    st.title('FAQs')
    st.markdown("""
        ## Frequently Asked Questions

        This section addresses some common questions about the Melanoma Detection App. If you have any other questions, feel free to reach out to us using the Feedback and Contact form.

        **Q: How accurate are the models used in this app?**
        - A: The accuracy of the models varies, as different architectures have different performance characteristics. You can check the Model Performance page for detailed metrics on accuracy, precision, recall, and AUC for each model.

        **Q: Can I trust the results of this app for medical diagnosis?**
        - A: This app is designed for educational and informational purposes only. The results should not be used as a substitute for professional medical advice. If you have any concerns about a skin lesion, please consult a qualified healthcare provider.

        **Q: What types of images can I upload for detection?**
        - A: You can upload both skin images and dermoscopy images for melanoma detection. The app will automatically detect the image type and use the appropriate model for classification.

        **Q: How do I interpret the prediction results?**
        - A: The app will classify the uploaded image as either Melanoma (Malignant) or Not Melanoma (Benign), along with a confidence score. This information is provided to help you understand the model's assessment, but should not be considered a definitive diagnosis.

        **Q: Is my uploaded image stored or used for other purposes?**
        - A: No, your uploaded images are not stored or used for any other purpose. They are only used for the current session's classification and are not retained or shared.
    """)

# Feedback and contact form
def feedback_form():
    st.title('Feedback and Contact')
    st.write("If you have any feedback, questions, or need support, please don't hesitate to reach out to us at 2adedd38@solent.ac.uk. We're here to help and improve the Melanoma Detection App.")

# Combine all pages into a single app
def run_app():
    st.sidebar.title('Navigation')
    pages = {
        "Introduction": main,
        "Model Performance": model_performance_page,
        "Visualizations": visualize_data,
        "Melanoma Detection": melanoma_detection,
        "Educational Resources": educational_resources,
        "FAQs": faq_section,
        "Feedback and Contact": feedback_form
    }

    selection = st.sidebar.radio("Go to", list(pages.keys()))
    pages[selection]()

    st.sidebar.markdown(disclaimer_text)

if __name__ == '__main__':
    run_app()
