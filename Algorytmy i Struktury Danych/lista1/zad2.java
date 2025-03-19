import java.util.Random;

class ListNodezad2 {
    int val;
    ListNodezad2 next;

    ListNodezad2(int val) {
        this.val = val;
        this.next = null;
    }
}

class CircularLinkedList {
    ListNodezad2 head;
    int size;

    CircularLinkedList() {
        this.head = null;
        this.size = 0;
    }

    void insert(int i) {
        ListNodezad2 newNode = new ListNodezad2(i);
        if (head == null) {
            head = newNode;
        } else {
            ListNodezad2 temp = head;
            while (temp.next != head) {
                temp = temp.next;
            }
            temp.next = newNode;
        }
        newNode.next = head;
        size++;
    }

    void merge(CircularLinkedList l1, CircularLinkedList l2) {
        if (l1.head == null) {
            head = l2.head;
        } else if (l2.head == null) {
            head = l1.head;
        } else {
            ListNodezad2 temp1 = l1.head;
            ListNodezad2 temp2 = l2.head;

            while (temp1.next != l1.head) {
                temp1 = temp1.next;
            }
            while (temp2.next != l2.head) {
                temp2 = temp2.next;
            }

            temp1.next = l2.head;
            temp2.next = l1.head;
            head = l1.head;
        }
        size = l1.size + l2.size;
    }

    int wyszukiwanie(int key) {
        if (head == null) {
            return 0;
        }

        int cost = 0;
        ListNodezad2 current = head;
        do {
            cost++;
            if (current.val == key) {
                return cost;
            }
            current = current.next;
        } while (current != head);

        return cost;
    }

    void display() {
        if (head == null) {
            System.out.println("List is empty");
            return;
        }
        ListNodezad2 current = head;
        do {
            System.out.print(current.val + " ");
            current = current.next;
        } while (current != head);
        System.out.println();
    }
}

public class zad2 {
    public static void main(String[] args) {
        CircularLinkedList list1 = new CircularLinkedList();
        CircularLinkedList list2 = new CircularLinkedList();


        for (int i = 10; i < 20; i++) {
            list1.insert(i);
        }


        for (int i = 20; i < 30; i++) {
            list2.insert(i);
        }


        System.out.println("Lista 1:");
        list1.display();
        System.out.println("Lista 2:");
        list2.display();


        list1.merge(list1, list2);


        System.out.println("Lista1 i Lista 2 połączone:");
        list1.display();


        CircularLinkedList list3 = new CircularLinkedList();
        Random random = new Random();
        int[] T = new int[10000];
        for (int i = 0; i < T.length; i++) {
            T[i] = random.nextInt(100001); // losowanie liczby całkowitej z przedziału [0, 100000]
            list3.insert(T[i]);
        }

        int suma1 = 0;
        int suma2 = 0;
        int wyszukiwania = 1000;
        for (int i = 0; i < wyszukiwania; i++) {

            int losliczba1 = T[random.nextInt(T.length)];
            suma1 += list3.wyszukiwanie(losliczba1);


            int losliczba2 = random.nextInt(100001);
            suma2 += list3.wyszukiwanie(losliczba2);
        }


        double avgCostOnList = (double) suma1 / wyszukiwania;
        double avgCostOnRange = (double) suma2 / wyszukiwania;

        System.out.println("Średnia koszt jednego wyszukania liczby z listy: " + avgCostOnList);
        System.out.println("Średnia koszt jednego wyszukania liczby z listy[0, 100000]: " + avgCostOnRange);
    }
}
