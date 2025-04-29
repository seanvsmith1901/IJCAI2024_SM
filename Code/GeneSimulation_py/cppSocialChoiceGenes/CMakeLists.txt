cmake_minimum_required(VERSION 3.30)
project(cppSocialChoiceGenes)

set(CMAKE_CXX_STANDARD 20)

add_executable(cppSocialChoiceGenes GeneticAlgorithm.cpp
        socialChoiceSim.cpp
        socialChoiceSim.h
        gameTheoryBot.cpp
        gameTheoryBot.h
        Chromosome.cpp
        Chromosome.h
        GeneticAlgorithm.cpp
        GeneticAlgorithm.h
        Logger.cpp
        Logger.h
        SocialChoiceTest.cpp
        GreedyBot.cpp
        GreedyBot.h)
