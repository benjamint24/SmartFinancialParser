#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import datacreation
import datacleaning
import dataanalysis


def main():
    while True:
        print("\n==============================")
        print("Welcome to Benjamin's data parser!")
        print("==============================\n")

        # 1) CREATE
        if datacreation.creation_demo() == False:
            break

        # 2) CLEAN
        if datacleaning.cleaning_demo() == False:
            break

        # 3) ANALYZE
        dataanalysis.analysis_demo()

        # REPEAT?
        print("\nRun the entire pipeline again with new data? (y/n)")
        choice = input(">> ").strip().lower()

        if choice != "y":
            break
    
    #breaks either due to done with parser or error
    print("\nExiting pipeline. Goodbye.")


if __name__ == "__main__":
    main()


# In[ ]:




