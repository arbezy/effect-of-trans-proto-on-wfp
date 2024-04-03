

def main():
    fp = "C:/Users/andre/Uni_Documents/Dissertation/list-of-websites-to-fp/URLs-to-fp.txt"
    with open(fp) as file:
        i = 1
        for line in file:
            newline = "host.docker.internal:2020/2019-top-unis/" + line.lstrip("https://").rstrip("\n")
            print(newline)
        
        
main()
