import string


def count_words_in_file(file_path):
    # Step 1: Read the file content
    with open(file_path, "r") as file:
        content = file.read().lower()  # Normalize to lowercase

    # Step 2: Remove punctuation
    content = content.translate(str.maketrans("", "", string.punctuation))

    # Step 3: Split content into words
    words = content.split()

    # Step 4: Count occurrences using a dictionary
    word_count = {}
    for word in words:
        if word in word_count:
            word_count[word] += 1
        else:
            word_count[word] = 1

    # Step 5: Sort the dictionary by word frequency
    sorted_word_count = sorted(
        word_count.items(), key=lambda item: item[1], reverse=True
    )

    # Step 6: Print results
    for word, count in sorted_word_count:
        print(f"{word}: {count}")


# Example use (uncomment the line below to run):
# count_words_in_file('example.txt')
