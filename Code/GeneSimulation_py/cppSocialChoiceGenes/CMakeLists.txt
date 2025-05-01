cmake_minimum_required(VERSION 3.30)
project(cppSocialChoiceGenes)

set(CMAKE_CXX_STANDARD 20)

add_executable(cppSocialChoiceGenes GeneticStuff/GeneticAlgorithm.cpp
        SocialChoiceStuff/SocialChoiceSim.cpp
        SocialChoiceStuff/SocialChoiceSim.h
        Bots/GameTheoryBot.cpp
        Bots/GameTheoryBot.h
        GeneticStuff/Chromosome.cpp
        GeneticStuff/Chromosome.h
        GeneticStuff/GeneticAlgorithm.cpp
        GeneticStuff/GeneticAlgorithm.h
        LoggingSuite/Logger.cpp
        LoggingSuite/Logger.h
        SocialChoiceTest.cpp
        Bots/GreedyBot.cpp
        Bots/GreedyBot.h
        Bots/ParentBot.h)
