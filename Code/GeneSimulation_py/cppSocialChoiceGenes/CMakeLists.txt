cmake_minimum_required(VERSION 3.30)
project(cppSocialChoiceGenes)

set(CMAKE_CXX_STANDARD 20)

add_executable(cppSocialChoiceGenes main.cpp
        socialChoiceSim.cpp
        socialChoiceSim.h
        gameTheoryBot.cpp
        gameTheoryBot.h)
