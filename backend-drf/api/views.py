from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import StockPredictionSerializer
from rest_framework.response import Response
from rest_framework import status
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import os
from django.conf import settings
from .utils import save_plot
from sklearn.preprocessing import MinMaxScaler
from keras.models import load_model
from sklearn.metrics import mean_squared_error, r2_score




class StockPredictionAPIView(APIView):
  def post(self, request):
    serializer = StockPredictionSerializer(data=request.data)
    if serializer.is_valid():
      ticker = serializer.validated_data['ticker']

      # Fetch the data from yfinance
      now = datetime.now()
      start = datetime(now.year-10, now.month, now.day)
      end = now
      df = yf.download(ticker, start, end)
      #print(df.head(5))
      if df.empty:
        return Response({'error': 'Ticker not found or no data available',
                         'status' : status.HTTP_404_NOT_FOUND})

      df  = df.reset_index()
      # Generate Basic Plot
      plt.switch_backend('Agg')
      plt.style.use('ggplot')
      plt.figure(figsize=(12,5))
      plt.plot(df.Close, label='Close Price')
      plt.title(f'Closing Price of {ticker}')
      plt.xlabel('Dyas')
      plt.ylabel('Price')
      plt.legend()
      # Save the plot to a file
      plot_img_path = f'{ticker}_plot.png'
      plot_img = save_plot(plot_img_path)


      # 100 Days moving avarage
      ma100 = df.Close.rolling(100).mean()
      plt.switch_backend('Agg')
      plt.style.use('ggplot')
      plt.figure(figsize=(12,5))
      plt.plot(df.Close, label='Close Price', color='blue')
      plt.plot(ma100, label='100 Days Moving Average', color='red')
      plt.title(f'Closing Price of {ticker}')
      plt.xlabel('Dyas')
      plt.ylabel('Price')
      plt.legend()
      plot_img_path = f'{ticker}_100_dma.png'
      plot_100_dma = save_plot(plot_img_path)

      # 200 Days moving avarage
      ma200 = df.Close.rolling(200).mean()
      plt.switch_backend('Agg')
      plt.style.use('ggplot')
      plt.figure(figsize=(12,5))
      plt.plot(df.Close, label='Close Price', color='blue')
      plt.plot(ma100, label='100 Days Moving Average', color='red')
      plt.plot(ma200, label='200 Days Moving Average', color='green')
      plt.title(f'Closing Price of {ticker}')
      plt.xlabel('Dyas')
      plt.ylabel('Price')
      plt.legend()
      plot_img_path = f'{ticker}_200_dma.png'
      plot_200_dma = save_plot(plot_img_path)

      # Splitting data into Training and Testing
      data_training = pd.DataFrame(df.Close[0:int(len(df)*0.7)])
      data_testing = pd.DataFrame(df.Close[int(len(df)*0.7): int(len(df))])

      # Scaling down the data between 0 and 1
      scaler = MinMaxScaler(feature_range=(0,1))

      # Load ML Model
      model = load_model('stock_prediction_model.keras')

      # Preparing the Test data
      past_100_days  = data_training.tail(100)
      final_df = pd.concat([past_100_days, data_testing], ignore_index=True)
      input_data = scaler.fit_transform(final_df)
      x_test = []
      y_test = []


      for i in range(100, input_data.shape[0]):
        x_test.append(input_data[i-100: i])
        y_test.append(input_data[i, 0])
      x_test , y_test = np.array(x_test) , np.array(y_test)

      # Making Predictions
      y_predict = model.predict(x_test)

      # Revert the scaled prices to original prices
      y_predict = scaler.inverse_transform(y_predict.reshape(-1,1)).flatten()
      y_test = scaler.inverse_transform(y_test.reshape(-1,1)).flatten()

      # Plot the final predictions
      plt.switch_backend('Agg')
      plt.style.use('ggplot')
      plt.figure(figsize=(12,5))
      plt.plot(y_test, label='Original Price', color='blue')
      plt.plot(y_predict, label='Predicted Price', color='red')
      plt.title(f'Final Prediction for {ticker}')
      plt.xlabel('Dyas')
      plt.ylabel('Price')
      plt.legend()
      plot_img_path = f'{ticker}_final_prediction.png'
      plot_prediction = save_plot(plot_img_path)

      # Model Evaluation
      # Mean Squared Error (MSE)
      mse = mean_squared_error(y_test, y_predict)

      # Root Mean Squared Error (RMSE)
      rmse = np.sqrt(mse)

      # R-squared (R2)
      r2 = r2_score(y_test, y_predict)

      return Response({'status': 'success',
                       'plot_img': plot_img,
                       'plot_100_dma': plot_100_dma,
                       'plot_200_dma': plot_200_dma,
                       'plot_prediction': plot_prediction,
                       'mse': mse,
                       'rmse': rmse,
                        'r2': r2},)