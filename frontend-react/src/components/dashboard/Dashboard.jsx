import {useEffect, useState} from 'react'
import axios from 'axios'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faSpinner } from '@fortawesome/free-solid-svg-icons'
import axiosInstance from '../../axiosInstance'

const Dashboard = () => {
  useEffect(() => {
    const fatchProtectedData = async () => {
      try {
        const response = await axiosInstance.get('/protected-view/') 
        console.log('Protected data:', response.data)
      }catch (error) {
        console.error("Error finding" ,error)
      }
    }
    fatchProtectedData();
  }, [])
  return (
    <>
        <h1 className='text-light'>Hello, world</h1>
    </>
  )
}

export default Dashboard