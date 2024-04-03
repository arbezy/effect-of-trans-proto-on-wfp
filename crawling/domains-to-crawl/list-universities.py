# Script to clean a list of universities, countries and numbers to just a list of universities
# This was used to copy and paste a uni ranking table into a text file and then clean out all the irrelevent info
# It would also be possible to use a webscraper but this seemed a bit overkill

def main():
    fp = "C:/Users/andre/Uni_Documents/Dissertation/list-of-websites-to-fp/Uni-cities.txt"
    countries = ['United Kingdom', 'United States', 'Switzerland','China', 'Canada', 'Singapore',' Austrailia','Australia', 'France', 'Germany', 'Sweden', 'Hong Kong', 'Japan','Belgium','Netherlands','South Korea', 'Finland']
    with open(fp) as file:
        i = 1
        for line in file:
            line = line.rstrip()
            
            if (not line in countries) and (not line.replace('.','',1).isdigit()):
                print(f"{i}. {line}")
                i += 1
        
main()