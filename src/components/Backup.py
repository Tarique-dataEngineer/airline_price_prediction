import sys
from dataclasses import dataclass

import numpy as np 
import pandas as pd
from sklearn.compose import ColumnTransformer   #for creating a pipeline for reuse
from sklearn.impute import SimpleImputer    # for handling missing values
from sklearn.pipeline import Pipeline    # for pipelines
from sklearn.preprocessing import OneHotEncoder,StandardScaler 
import os 

from src.exception import CustomException
from src.logger import logging

from src.utils import save_object

@dataclass
class DataTransformationConfig:
    preprocessor_obj_file_path=os.path.join('artifacts',"proprocessor.pkl")

class DataTransformation:
    def __init__(self):
        self.data_transformation_config=DataTransformationConfig()

    def get_data_transformer_object(self):
        '''
        This function is responsible for data trnasformation
        
        '''
        try:
            numerical_columns = ["duration", "days_left"]
            categorical_columns = ["airline",  
                                   "source_city", 
                                   "departure_time", 
                                   "stops",
                                   "arrival_time", 
                                   "destination_city", 
                                   "class"]

            num_pipeline= Pipeline(
                steps=[
                ("imputer",SimpleImputer(strategy="median")),
                ("scaler",StandardScaler())

                ]
            )

            cat_pipeline=Pipeline(

                steps=[
                ("imputer",SimpleImputer(strategy="most_frequent")),
                ("one_hot_encoder",OneHotEncoder()),
                ("scaler",StandardScaler(with_mean=False))
                ]

            )

            logging.info(f"Categorical columns: {categorical_columns}")
            logging.info(f"Numerical columns: {numerical_columns}")

            preprocessor=ColumnTransformer(
                [
                ("num_pipeline",num_pipeline,numerical_columns),
                ("cat_pipelines",cat_pipeline,categorical_columns)

                ]


            )

            return preprocessor
        
        except Exception as e:
            raise CustomException(e,sys)
        
    def initiate_data_transformation(self,train_path,test_path):

        try:
            train_df=pd.read_csv(train_path)
            test_df=pd.read_csv(test_path)

            logging.info("Read train and test data completed")

            logging.info("Obtaining preprocessing object")

            preprocessing_obj=self.get_data_transformer_object()

            target_column_name="price"
            numerical_columns = ["duration", "days_left"]

            input_feature_train_df=train_df.drop(columns=[target_column_name],axis=1)
            target_feature_train_df=train_df[target_column_name]

            input_feature_test_df=test_df.drop(columns=[target_column_name],axis=1)
            target_feature_test_df=test_df[target_column_name]

            logging.info(
                f"Applying preprocessing object on training dataframe and testing dataframe."
            )


            input_feature_train_arr=preprocessing_obj.fit_transform(input_feature_train_df)
            input_feature_test_arr=preprocessing_obj.transform(input_feature_test_df)

            logging.info(f"the input freature train arr shape is {input_feature_train_arr.shape}".format())
            logging.info(f"the input freature test arr shape is {input_feature_test_arr.shape}".format())

            target_feature_train_arr=np.array(target_feature_train_df)
            target_feature_test_arr=np.array(target_feature_test_df)

            target_feature_train_arr=target_feature_train_arr.reshape(-1,1)
            target_feature_test_arr=target_feature_test_arr.reshape(-1,1)

            logging.info(f"target feature train arr shape {target_feature_train_arr.shape}".format())
            logging.info(f"target feature test arr shape {target_feature_test_arr.shape}".format())


            train_arr = np.c_[
                input_feature_train_arr, target_feature_train_arr
            ]

            test_arr = np.c_[input_feature_test_arr, target_feature_test_arr]

            logging.info(f"Saved preprocessing object.")

            save_object(

                file_path=self.data_transformation_config.preprocessor_obj_file_path,
                obj=preprocessing_obj

            )

            return (
                train_arr,
                test_arr,
                self.data_transformation_config.preprocessor_obj_file_path,
            )
        except Exception as e:
            raise CustomException(e,sys)