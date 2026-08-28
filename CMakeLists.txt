cmake_minimum_required(VERSION 4.2)
project(IJCAI2024_SM)

set(CMAKE_CXX_STANDARD 14)

include_directories(Code/GeneSimulation_cpp)

add_executable(IJCAI2024_SM
        Code/GeneSimulation_cpp/AbstractAgent.h
        Code/GeneSimulation_cpp/assassinAgent.h
        Code/GeneSimulation_cpp/CommunityEvaluation.h
        Code/GeneSimulation_cpp/CoOpAgent.h
        Code/GeneSimulation_cpp/createRandomNums.cpp
        Code/GeneSimulation_cpp/defs.h
        Code/GeneSimulation_cpp/GeneAgent.h
        Code/GeneSimulation_cpp/HumanAgent.h
        Code/GeneSimulation_cpp/JHGEngine.h
        Code/GeneSimulation_cpp/main.cpp
        Code/GeneSimulation_cpp/logger.h)
