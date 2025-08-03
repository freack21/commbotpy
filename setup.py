from setuptools import setup, find_packages

setup(
  name="commbotpy",
  version="0.0.0",
  packages=find_packages(),
  install_requires=["pyserial"],
  author="Fikri",
  author_email="fixri2104@gmail.com",
  description="Lightweight serial comms lib between Python and Arduino using pub/sub like ROS.",
  keywords=["arduino", "serial", "robotics", "communication", "pubsub"],
  classifiers=[
    "Programming Language :: Python :: 3",
    "Operating System :: OS Independent",
  ],
)
