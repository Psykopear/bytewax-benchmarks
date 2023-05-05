for i in `ls results`; do
  img=`echo $i | cut -d'.' -f1`
  python plot.py results/"$i" -o results/"$img".png
done
