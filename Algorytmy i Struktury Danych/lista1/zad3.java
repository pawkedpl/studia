import java.util.Random;

class ListNodezad3 {
    int val;
    ListNodezad3 next;
    ListNodezad3 prev;

    ListNodezad3(int val) {
        this.val = val;
        this.next = null;
        this.prev = null;
    }
}

class CircularDoublyLinkedList {
    ListNodezad3 head;
    int size;

    CircularDoublyLinkedList() {
        this.head = null;
        this.size = 0;
    }

    void insert(int i) {
        ListNodezad3 newNode = new ListNodezad3(i);
        if (head == null) {
            head = newNode;
        } else {
            ListNodezad3 temp = head;
            while (temp.next != head) {
                temp = temp.next;
            }
            temp.next = newNode;
            newNode.prev = temp;
        }
        newNode.next = head;
        head.prev = newNode;
        size++;
    }

    void merge(CircularDoublyLinkedList l1, CircularDoublyLinkedList l2) {
        if (l1.head == null) {
            head = l2.head;
        } else if (l2.head == null) {
            head = l1.head;
        } else {
            ListNodezad3 temp1 = l1.head;
            ListNodezad3 temp2 = l2.head;

            while (temp1.next != l1.head) {
                temp1 = temp1.next;
            }
            while (temp2.next != l2.head) {
                temp2 = temp2.next;
            }

            temp1.next = l2.head;
            temp2.next = l1.head;
            l1.head.prev = temp2;
            l2.head.prev = temp1;
            head = l1.head;
        }
        size = l1.size + l2.size;
    }

    int wyszukiwanie(int key) {
        if (head == null) {
            return 0;
        }

        int cost = 0;
        ListNodezad3 current = head;
        Random random = new Random();

        // Losowe wybranie kierunku
        boolean forward = random.nextBoolean();
        if (!forward) {
            current = current.prev;
        }

        do {
            cost++;
            if (current.val == key) {
                return cost;
            }
            if (forward) {
                current = current.next;
            } else {
                current = current.prev;
            }
        } while (current != head);

        return cost;
    }

    void display() {
        if (head == null) {
            System.out.println("List is empty");
            return;
        }
        ListNodezad3 current = head;
        do {
            System.out.print(current.val + " ");
            current = current.next;
        } while (current != head);
        System.out.println();
    }
}

public class zad3 {
    public static void main(String[] args) {
        CircularDoublyLinkedList list1 = new CircularDoublyLinkedList();
        CircularDoublyLinkedList list2 = new CircularDoublyLinkedList();

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

        // Zadanie b)
        CircularDoublyLinkedList list3 = new CircularDoublyLinkedList();
        Random random = new Random();
        int[] T = new int[10000];
        for (int i = 0; i < T.length; i++) {
            T[i] = random.nextInt(100001);
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
